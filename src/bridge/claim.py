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
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone

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


def _check_resource(store: Store, task_id: str, moment: datetime) -> None:
    """Ressourcenregel: kein anderer aktiver Claim auf (repository, remote, branch)."""
    remote = _remote_url(store)
    mine = _resource_key(store, task_id, remote)
    if not store.results_dir.is_dir():
        return
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
    """Legt den Claim an, uebernimmt einen abgelaufenen oder verlaengert den eigenen."""
    _require_owner(actor, machine)
    _check_lease(lease_seconds)
    moment = _now(now)
    with _Locked(store):
        store.load_task(task_id)  # unbekannter Auftrag -> StoreError
        current = get_claim(store, task_id)
        if current is None:
            _check_resource(store, task_id, moment)
            doc = _write(store, task_id, actor, machine, lease_seconds, moment)
            reason = f"claim lease={lease_seconds}s"
        elif _is_owner(current, actor, machine):
            doc = _write(store, task_id, actor, machine, lease_seconds, moment,
                         claimed_at=current.get("claimed_at"))
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
        return doc


def renew(store: Store, task_id: str, actor: str, machine: str, lease_seconds: int, *,
          now: datetime | None = None) -> dict:
    """Verlaengert die Lease ab jetzt; nur der Besitzer."""
    _require_owner(actor, machine)
    _check_lease(lease_seconds)
    moment = _now(now)
    with _Locked(store):
        current = get_claim(store, task_id)
        if current is None:
            raise ClaimError(f"Kein Claim fuer {task_id}.")
        if not _is_owner(current, actor, machine):
            raise ClaimError(
                f"CLAIM_CONFLICT: {task_id} gehoert {_describe(current)}, nicht "
                f"{actor}@{machine}.")
        return _write(store, task_id, actor, machine, lease_seconds, moment,
                      claimed_at=current.get("claimed_at"))


def release(store: Store, task_id: str, actor: str, machine: str, *,
            now: datetime | None = None) -> None:
    """Gibt den Claim frei; nur der Besitzer (abgelaufene Claims: jeder)."""
    _require_owner(actor, machine)
    moment = _now(now)
    with _Locked(store):
        current = get_claim(store, task_id)
        if current is None:
            raise ClaimError(f"Kein Claim fuer {task_id}.")
        if not _is_owner(current, actor, machine) and not _is_expired(current, moment):
            raise ClaimError(
                f"CLAIM_CONFLICT: {task_id} gehoert {_describe(current)}, nicht "
                f"{actor}@{machine}.")
        _path(store, task_id).unlink()
