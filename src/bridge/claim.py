"""Claim/Lease je Auftrag (BRIDGE-0061 Teil B, Stufe B / Gate G3).

Ein Claim reserviert einen Auftrag fuer einen Akteur auf einer Maschine, befristet
durch eine Lease (``expires_at``). Ablage: ``results/<id>/claim.json``. Alle
Schreibzugriffe laufen unter dem Writer-Lock (``bridge.lock``).

- ``claim``:   fremder aktiver Claim -> ``ClaimError`` (CLAIM_CONFLICT); abgelaufener
               Claim darf uebernommen werden (Audit-Reason nennt den Vorbesitzer);
               eigener Claim wird wie ``renew`` verlaengert.
               Ressourcenregel (BRIDGE-0063, docs/concepts/ENTSCHEIDUNG-RESSOURCENREGEL.md):
               ein neuer Claim wird abgelehnt (RESOURCE_CONFLICT), wenn ein anderer
               Auftrag mit aktivem Claim denselben Schluessel (repository, remote, branch) hat.
- ``renew``:   nur der Besitzer verlaengert die Lease.
- ``release``: nur der Besitzer gibt frei (ein abgelaufener Claim darf von jedem
               entfernt werden).

Audit: ``claim`` (neu und Uebernahme) schreibt ``TASK_CLAIMED`` mit ``reason``
(ohne Zustandswechsel des Auftrags). ``renew``/``release`` schreiben kein Audit.
Zeiten sind UTC im Format ``%Y-%m-%dT%H:%M:%SZ``; ``now`` ist fuer Tests injizierbar.

Seit BRIDGE-0078 ist ``claim.json`` versioniert und damit klonuebergreifend
wirksam (vorher nur klonlokal sichtbar, siehe ``ENTSCHEIDUNG-CLAIM-SICHTBARKEIT.md``).
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone

import yaml

from bridge import gitops
from bridge import lock as _lock
from bridge.store import Store, StoreError, _atomic_write

CLAIM_FILE = "claim.json"
DEFAULT_LEASE_SECONDS = 3600
_TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class ClaimError(StoreError):
    """Claim/Lease-Regel verletzt (fail-closed)."""


def _fmt(moment: datetime) -> str:
    return moment.strftime(_TS_FORMAT)


def _parse(text) -> datetime:
    try:
        return datetime.strptime(text, _TS_FORMAT).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise ClaimError(f"Claim-Zeitstempel unbrauchbar: {text!r}") from exc


def _now(now) -> datetime:
    return (now or datetime.now(timezone.utc)).replace(microsecond=0)


def _path(store: Store, task_id: str):
    task_id = store._check_id(task_id)
    return store._in_root(store.results_dir / task_id / CLAIM_FILE)


def _check_lease(lease_seconds) -> int:
    if isinstance(lease_seconds, bool) or not isinstance(lease_seconds, int) or lease_seconds <= 0:
        raise ClaimError(f"lease_seconds muss eine positive ganze Zahl sein: {lease_seconds!r}")
    return lease_seconds


def _require_owner(actor, machine) -> None:
    if not actor:
        raise ClaimError("actor fehlt.")
    if not machine:
        raise ClaimError("machine fehlt.")


def get_claim(store: Store, task_id: str) -> dict | None:
    """Liest den Claim (``None`` wenn keiner existiert). Rein lesend."""
    path = _path(store, task_id)
    if not path.exists():
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ClaimError(f"claim.json unbrauchbar: {path} ({exc})") from exc
    if not isinstance(doc, dict) or not all(
            k in doc for k in ("actor", "machine", "expires_at")):
        raise ClaimError(f"claim.json unvollstaendig: {path}")
    _parse(doc["expires_at"])
    return doc


def _is_expired(doc: dict, now: datetime) -> bool:
    return _parse(doc["expires_at"]) <= now


def _local_claim_text(store: Store, task_id: str) -> str | None:
    """Rohinhalt der LOKALEN ``claim.json`` (``None`` wenn keine existiert).
    Grundlage fuer das Push-Race-Rollback - bewusst getrennt von
    ``_synced_claim``, die fuer die Entscheidungslogik den Remote-Stand
    bevorzugt: zurueckgerollt wird immer auf den tatsaechlichen lokalen
    Vorzustand, nie auf einen nur gelesenen Fremdstand."""
    try:
        return _path(store, task_id).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _synced_claim(store: Store, task_id: str) -> dict | None:
    """Liefert den massgeblichen aktuellen Claim fuer die Entscheidungslogik
    in ``claim``/``renew``/``release`` (BRIDGE-0078).

    Bei vorhandenem Git-Repo wird vorher gefetcht und der Stand aus
    ``origin/main`` bevorzugt - das ist seit BRIDGE-0078 die Cross-Klon-
    Quelle der Wahrheit, nicht die ggf. veraltete lokale Datei (ein anderer
    Klon kann laengst geclaimt/verlaengert/freigegeben haben, ohne dass
    dieser Klon je ``pull``/``checkout`` dafuer ausgefuehrt hat). Kein Git-
    Repo (z. B. hermetischer Test) oder kein Fremdstand gefunden: lokaler
    Stand wie vor BRIDGE-0078.
    """
    if _has_git_repo(store):
        fetch_result = gitops.git_fetch(store.root)
        if fetch_result["error"]:
            raise ClaimError(
                f"RESOURCE_CONFLICT-Pruefung fehlgeschlagen (git fetch): {fetch_result['error']}")
        # Best-effort Catch-up: lokalen main-Stand auf origin/main vorziehen,
        # SOLANGE das ein reiner Fast-Forward ist (noch vor jedem eigenen
        # Schreiben hier, Arbeitsbaum also noch unberuehrt). Ergebnis bewusst
        # ignoriert - schlaegt es fehl, bleibt der alte Lokalstand, und der
        # spaetere Commit/Push greift wie zuvor auf den Rebase-Ausgleich
        # zurueck. Ohne dieses Vorziehen wuerde ein claim.json-Uebernahme-
        # Commit auf einem veralteten Elternstand sonst einen echten
        # Add/Add-Konflikt beim Rebase ausloesen, auch wenn inhaltlich nur
        # 'alt durch neu ersetzen' gemeint ist.
        _git(store, "merge", "--ff-only", "origin/main")
        remote = _remote_claim(store, task_id)
        if remote is not None:
            return remote
    return get_claim(store, task_id)


def _is_owner(doc: dict, actor, machine) -> bool:
    return doc["actor"] == actor and doc["machine"] == machine


def _describe(doc: dict) -> str:
    return f"{doc['actor']}@{doc['machine']} (bis {doc['expires_at']})"


def _write(store: Store, task_id: str, actor, machine, lease_seconds, now, claimed_at=None):
    doc = {
        "actor": actor,
        "machine": machine,
        "claimed_at": claimed_at or _fmt(now),
        "expires_at": _fmt(now + timedelta(seconds=lease_seconds)),
        "lease_seconds": lease_seconds,
    }
    _atomic_write(_path(store, task_id), json.dumps(doc, indent=2) + "\n")
    return doc


def _remote_url(store: Store) -> str:
    """``git remote get-url origin`` im Repo-Root; ``<none>`` wenn nicht ermittelbar."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(store.root), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return "<none>"
    return proc.stdout.strip() or "<none>" if proc.returncode == 0 else "<none>"


def _resource_key(store: Store, task_id: str, remote: str) -> tuple:
    task = store.load_task(task_id)
    return (task.get("repository"), remote, task.get("branch"))


def _has_git_repo(store: Store) -> bool:
    return (store.root / ".git").exists()


def _git(store: Store, *args, timeout=30):
    """``git -C <store.root> <args>``, nie geworfen (``check=False``)."""
    return subprocess.run(
        ["git", "-C", str(store.root), *args],
        capture_output=True, text=True, timeout=timeout, check=False)


def _remote_show(store: Store, path: str) -> str | None:
    """``git show origin/main:<path>``; ``None`` wenn der Pfad dort nicht
    existiert (oder gar kein Git-Repo vorhanden ist)."""
    r = _git(store, "show", f"origin/main:{path}")
    return r.stdout if r.returncode == 0 else None


def _list_remote_claim_ids(store: Store) -> list[str]:
    """Alle ``task_id``, die unter ``origin/main`` eine ``claim.json`` haben
    (BRIDGE-0078, Grundlage der klonuebergreifenden Sichtbarkeit)."""
    r = _git(store, "ls-tree", "-r", "--name-only", "origin/main", "--", "results/")
    if r.returncode != 0:
        # Kein origin/main bekannt (frisches Repo ohne Remote-Branch o.ae.) -
        # keine Fremd-Claims feststellbar, nichts zu melden.
        return []
    ids = []
    for line in r.stdout.splitlines():
        parts = line.strip().split("/")
        if len(parts) == 3 and parts[0] == "results" and parts[2] == CLAIM_FILE:
            ids.append(parts[1])
    return ids


def _remote_claim(store: Store, task_id: str) -> dict | None:
    text = _remote_show(store, f"results/{task_id}/{CLAIM_FILE}")
    if text is None:
        return None
    try:
        doc = json.loads(text)
    except ValueError as exc:
        raise ClaimError(f"Remote claim.json unbrauchbar fuer {task_id}: {exc}") from exc
    if not isinstance(doc, dict) or not all(
            k in doc for k in ("actor", "machine", "expires_at")):
        raise ClaimError(f"Remote claim.json unvollstaendig fuer {task_id}.")
    _parse(doc["expires_at"])
    return doc


def _remote_resource_key(store: Store, task_id: str) -> tuple | None:
    """``(repository, branch)`` des Auftrags aus ``origin/main:tasks/<id>/task.yaml``,
    oder ``None`` wenn dort kein Auftrag mit dieser ID liegt."""
    text = _remote_show(store, f"tasks/{task_id}/task.yaml")
    if text is None:
        return None
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ClaimError(f"Remote task.yaml unbrauchbar fuer {task_id}: {exc}") from exc
    if not isinstance(doc, dict):
        raise ClaimError(f"Remote task.yaml unbrauchbar fuer {task_id}.")
    return (doc.get("repository"), doc.get("branch"))


def _check_resource(store: Store, task_id: str, moment: datetime) -> None:
    """Ressourcenregel: kein anderer aktiver Claim auf (repository, remote, branch).

    Seit BRIDGE-0078 zusaetzlich zum lokalen Bestand gegen den frisch
    gefetchten ``origin/main``-Stand geprueft (klonuebergreifende
    Sichtbarkeit, siehe ``ENTSCHEIDUNG-CLAIM-SICHTBARKEIT.md`` Option B).
    Ohne Git-Repo (z. B. hermetischer Test): nur der lokale Bestand wie vor
    BRIDGE-0078 - kein Netzwerkzugriff moeglich, also auch keine Pruefung.
    """
    remote = _remote_url(store)
    mine = _resource_key(store, task_id, remote)
    if store.results_dir.is_dir():
        for entry in sorted(store.results_dir.iterdir()):
            if entry.name == task_id or not (entry / CLAIM_FILE).is_file():
                continue
            other = get_claim(store, entry.name)
            if other is None or _is_expired(other, moment):
                continue
            if _resource_key(store, entry.name, remote) == mine:
                raise ClaimError(
                    f"RESOURCE_CONFLICT: {task_id} kollidiert mit {entry.name} "
                    f"({_describe(other)}) auf {mine}.")

    if not _has_git_repo(store):
        return

    fetch_result = gitops.git_fetch(store.root)
    if fetch_result["error"]:
        raise ClaimError(
            f"RESOURCE_CONFLICT-Pruefung fehlgeschlagen (git fetch): {fetch_result['error']}")

    mine_remote_part = (mine[0], mine[2])  # (repository, branch) - ohne 'remote'
    for other_id in _list_remote_claim_ids(store):
        if other_id == task_id:
            continue
        other = _remote_claim(store, other_id)
        if other is None or _is_expired(other, moment):
            continue
        other_key = _remote_resource_key(store, other_id)
        # Claim ohne auffindbaren Auftrag im selben Fetch-Stand: konservativ
        # blockieren, nie weniger streng als bei bekanntem Schluessel (analog
        # dem '<none>'-Fallback in _remote_url).
        if other_key is None or other_key == mine_remote_part:
            raise ClaimError(
                f"RESOURCE_CONFLICT: {task_id} kollidiert mit {other_id} (origin/main) "
                f"({_describe(other)}) auf {mine}.")


_CLAIM_PUSH_RETRY_PATTERNS = ("rejected", "non-fast-forward", "fetch first")


def _restore(store: Store, task_id: str, previous_text: str | None) -> None:
    path = _path(store, task_id)
    if previous_text is None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    else:
        _atomic_write(path, previous_text)


def _branch_name(store: Store) -> str:
    r = _git(store, "rev-parse", "--abbrev-ref", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else ""


def _push_with_retry(store: Store, branch: str) -> tuple[bool, str | None]:
    """Ein ``git push``, mit genau einem Fetch+Rebase-Ausgleichsversuch bei
    Non-Fast-Forward (Muster wie ``gitops.git_commit``), aber beschraenkt
    auf den bereits lokal gemachten Claim-Commit.

    ``--autostash``: der Claim-Commit beruehrt bewusst nur ``claim.json``
    (siehe ``_sync_claim_commit``); ein parallel anstehender, nicht dazu-
    gehoeriger Audit-Eintrag (z. B. aus ``claim()``s eigenem Aufruf) bleibt
    dabei absichtlich uncommittet im Arbeitsbaum stehen. ``git rebase``
    verlangt aber einen vollstaendig sauberen Baum - ``--autostash`` legt
    so einen Rest automatisch zur Seite und holt ihn danach (auch nach
    einem ``--abort``) wieder zurueck, ohne ihn zu committen."""
    r = _git(store, "push", timeout=60)
    if r.returncode == 0:
        return True, None
    err = (r.stderr or r.stdout).strip()
    if not any(p in err.lower() for p in _CLAIM_PUSH_RETRY_PATTERNS):
        return False, err

    r_fetch = _git(store, "fetch", "origin", timeout=60)
    if r_fetch.returncode != 0:
        return False, f"fetch nach NFF fehlgeschlagen: {(r_fetch.stderr or r_fetch.stdout).strip()}"

    r_rebase = _git(store, "rebase", "--autostash", f"origin/{branch}")
    if r_rebase.returncode != 0:
        _git(store, "rebase", "--abort")
        return False, f"rebase fehlgeschlagen (Konflikt): {(r_rebase.stderr or r_rebase.stdout).strip()}"

    r2 = _git(store, "push", timeout=60)
    if r2.returncode != 0:
        return False, f"push nach Rebase fehlgeschlagen: {(r2.stderr or r2.stdout).strip()}"
    return True, None


def _sync_claim_commit(store: Store, task_id: str, verb: str, previous_text: str | None) -> None:
    """Committet+pusht AUSSCHLIESSLICH ``results/<task_id>/claim.json``
    (BRIDGE-0078) - unabhaengig davon, ob sonst noch etwas im Baum dirty ist
    (z. B. ein unabhaengig anstehender Audit-Eintrag; der wird hier bewusst
    NICHT committet, das uebernimmt die naechste reguläre ``--commit``-Aktion).

    Kein Git-Repo (z. B. hermetischer Test): no-op, der Claim bleibt
    klonlokal wie vor BRIDGE-0078.

    Push-Race-Rollback (Pflichtbestandteil): schlaegt Commit ODER Push fehl,
    wird der lokale Dateiinhalt exakt auf ``previous_text`` zurueckgesetzt
    (``None`` = Datei loeschen) und ``ClaimError`` mit ``RESOURCE_CONFLICT``
    geworfen - kein haengender lokaler Claim ohne Entsprechung im Repo.
    """
    if not _has_git_repo(store):
        return

    rel_path = f"results/{task_id}/{CLAIM_FILE}"
    branch = _branch_name(store)
    if branch != "main":
        _restore(store, task_id, previous_text)
        raise ClaimError(
            f"RESOURCE_CONFLICT: Claim-Synchronisation abgebrochen, Branch "
            f"ist {branch!r}, erwartet 'main'.")

    r = _git(store, "add", "--", rel_path)
    if r.returncode != 0:
        _restore(store, task_id, previous_text)
        raise ClaimError(f"RESOURCE_CONFLICT: git add fehlgeschlagen: "
                         f"{(r.stderr or r.stdout).strip()}")

    msg = f"Ops: {task_id} claim {verb} (Steuerchat-Aktion via CLI)"
    r = _git(store, "commit", "-m", msg)
    if r.returncode != 0:
        _git(store, "reset", "--", rel_path)
        _restore(store, task_id, previous_text)
        raise ClaimError(f"RESOURCE_CONFLICT: git commit fehlgeschlagen: "
                         f"{(r.stderr or r.stdout).strip()}")

    pushed, err = _push_with_retry(store, branch)
    if not pushed:
        # Lokalen Claim-Commit vollstaendig zurueckrollen (Commit + Arbeits-
        # kopie in einem Schritt) - danach entspricht der lokale Stand wieder
        # exakt dem zuletzt tatsaechlich im Repo sichtbaren Claim.
        _git(store, "reset", "--hard", "HEAD~1")
        raise ClaimError(f"RESOURCE_CONFLICT: Claim-Push fehlgeschlagen: {err}")


class _Locked:
    """Writer-Lock des Stores; WriterLockError -> ClaimError."""

    def __init__(self, store: Store):
        self._store = store
        self._cm = None

    def __enter__(self):
        self._cm = _lock.writer_lock(self._store.root, self._store.lock_timeout)
        try:
            self._cm.__enter__()
        except _lock.WriterLockError as exc:
            raise ClaimError(str(exc)) from exc
        return self

    def __exit__(self, *exc_info):
        return self._cm.__exit__(*exc_info)


def claim(store: Store, task_id: str, actor: str, machine: str, lease_seconds: int, *,
          now: datetime | None = None) -> dict:
    """Legt den Claim an, uebernimmt einen abgelaufenen oder verlaengert den eigenen.

    Seit BRIDGE-0078: committet+pusht die geschriebene ``claim.json`` (kein
    Git-Repo, z. B. hermetischer Test: no-op). Schlaegt das fehl, wird lokal
    zurueckgerollt und ``RESOURCE_CONFLICT`` geworfen - siehe
    ``_sync_claim_commit``.
    """
    _require_owner(actor, machine)
    _check_lease(lease_seconds)
    moment = _now(now)
    with _Locked(store):
        store.load_task(task_id)  # unbekannter Auftrag -> StoreError
        current = _synced_claim(store, task_id)
        previous_text = _local_claim_text(store, task_id)
        if current is None:
            _check_resource(store, task_id, moment)
            doc = _write(store, task_id, actor, machine, lease_seconds, moment)
            reason = f"claim lease={lease_seconds}s"
        elif _is_owner(current, actor, machine):
            doc = _write(store, task_id, actor, machine, lease_seconds, moment,
                         claimed_at=current.get("claimed_at"))
            _sync_claim_commit(store, task_id, "renew-self", previous_text)
            return doc
        elif _is_expired(current, moment):
            _check_resource(store, task_id, moment)
            doc = _write(store, task_id, actor, machine, lease_seconds, moment)
            reason = (f"takeover expired claim of {_describe(current)}; "
                      f"lease={lease_seconds}s")
        else:
            raise ClaimError(
                f"CLAIM_CONFLICT: {task_id} ist aktiv geclaimt von {_describe(current)}.")
        store.append_audit(store._event(
            "TASK_CLAIMED", task_id, actor=actor, machine=machine, reason=reason))
        _sync_claim_commit(store, task_id, "claim", previous_text)
        return doc


def renew(store: Store, task_id: str, actor: str, machine: str, lease_seconds: int, *,
          now: datetime | None = None) -> dict:
    """Verlaengert die Lease ab jetzt; nur der Besitzer.

    Seit BRIDGE-0078: committet+pusht wie ``claim()`` (Push-Race-Rollback
    siehe ``_sync_claim_commit``).
    """
    _require_owner(actor, machine)
    _check_lease(lease_seconds)
    moment = _now(now)
    with _Locked(store):
        current = _synced_claim(store, task_id)
        if current is None:
            raise ClaimError(f"Kein Claim fuer {task_id}.")
        if not _is_owner(current, actor, machine):
            raise ClaimError(
                f"CLAIM_CONFLICT: {task_id} gehoert {_describe(current)}, nicht "
                f"{actor}@{machine}.")
        previous_text = _local_claim_text(store, task_id)
        doc = _write(store, task_id, actor, machine, lease_seconds, moment,
                    claimed_at=current.get("claimed_at"))
        _sync_claim_commit(store, task_id, "renew", previous_text)
        return doc


def release(store: Store, task_id: str, actor: str, machine: str, *,
            now: datetime | None = None) -> None:
    """Gibt den Claim frei; nur der Besitzer (abgelaufene Claims: jeder).

    Seit BRIDGE-0078: committet+pusht die Entfernung der ``claim.json``.
    Schlaegt der Push fehl, wird der vorherige Claim lokal wiederhergestellt
    statt einen inkonsistenten Zustand zu hinterlassen (siehe
    ``_sync_claim_commit`` / ``ENTSCHEIDUNG-CLAIM-SICHTBARKEIT.md``).
    """
    _require_owner(actor, machine)
    moment = _now(now)
    with _Locked(store):
        current = _synced_claim(store, task_id)
        if current is None:
            raise ClaimError(f"Kein Claim fuer {task_id}.")
        if not _is_owner(current, actor, machine) and not _is_expired(current, moment):
            raise ClaimError(
                f"CLAIM_CONFLICT: {task_id} gehoert {_describe(current)}, nicht "
                f"{actor}@{machine}.")
        previous_text = _local_claim_text(store, task_id)
        try:
            _path(store, task_id).unlink()
        except FileNotFoundError:
            pass  # nur remote bekannt (noch nie lokal gefetcht/geschrieben) - nichts zu loeschen.
        _sync_claim_commit(store, task_id, "release", previous_text)
