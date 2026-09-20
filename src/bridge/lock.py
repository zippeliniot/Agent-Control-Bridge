"""Writer-Lock der Ablage (BRIDGE-0060 Teil B).

Serialisiert alle schreibenden Zugriffe auf den Store über die Lockdatei
``<root>/.acb-writer.lock`` (exklusives Anlegen per ``O_EXCL``, Inhalt: pid +
Zeit). Reentrant je Thread: verschachtelte Store-Aufrufe (z. B. ``set_status``
-> ``save_task`` -> ``append_audit``) halten den Lock nur einmal.

Ein alter Lock (> ``STALE_SECONDS``) wird NICHT automatisch gebrochen, sondern
als Fehler mit Hinweis gemeldet (fail-closed): ob der Halter tot ist, entscheidet
der Mensch.

Reine stdlib. Bewusst ohne Import aus ``bridge.store`` (Store importiert dieses
Modul; ``Store`` übersetzt ``WriterLockError`` in ``StoreError``).
"""

from __future__ import annotations

import json
import os
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

LOCK_NAME = ".acb-writer.lock"
STALE_SECONDS = 300
DEFAULT_TIMEOUT = 10.0
_POLL_SECONDS = 0.05


class WriterLockError(Exception):
    """Lock nicht erhältlich (Timeout) oder veraltet (fail-closed)."""


_state = threading.Lock()
_held: dict = {}  # (lock-pfad, thread-id) -> Verschachtelungstiefe


def lock_path(root) -> Path:
    return Path(root).resolve() / LOCK_NAME


def _holder_info(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return f"pid={data.get('pid')} seit {data.get('time')}"
    except (OSError, ValueError):
        return "Halter unbekannt"


def _age_seconds(path: Path):
    try:
        return time.time() - path.stat().st_mtime
    except OSError:
        return None  # zwischenzeitlich freigegeben


def _create(path: Path) -> bool:
    """Legt die Lockdatei exklusiv an. ``False`` wenn sie schon existiert."""
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        payload = {
            "pid": os.getpid(),
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
    except BaseException:
        try:
            os.unlink(str(path))
        except OSError:
            pass
        raise
    return True


@contextmanager
def writer_lock(root, timeout: float = DEFAULT_TIMEOUT, *,
                stale_after: float = STALE_SECONDS):
    """Kontextmanager: hält den Writer-Lock für ``root``.

    Wartet bis ``timeout`` Sekunden auf einen fremden Halter
    (-> ``WriterLockError``). Ist die Lockdatei älter als ``stale_after``
    Sekunden, wird sofort ``WriterLockError`` mit Hinweis geworfen; die Datei
    bleibt unangetastet.
    """
    path = lock_path(root)
    key = (str(path), threading.get_ident())

    with _state:
        depth = _held.get(key, 0)
        if depth:
            _held[key] = depth + 1
    if depth:
        try:
            yield
        finally:
            with _state:
                _held[key] -= 1
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    while not _create(path):
        age = _age_seconds(path)
        if age is not None and age > stale_after:
            raise WriterLockError(
                f"Veralteter Writer-Lock ({age:.0f} s alt, {_holder_info(path)}): "
                f"{path}. Nicht automatisch gebrochen - prüfen, ob der Halter "
                f"noch läuft, und die Datei sonst von Hand entfernen."
            )
        if time.monotonic() >= deadline:
            raise WriterLockError(
                f"Writer-Lock nach {timeout:g} s nicht erhalten "
                f"({_holder_info(path)}): {path}"
            )
        time.sleep(_POLL_SECONDS)

    with _state:
        _held[key] = 1
    try:
        yield
    finally:
        with _state:
            _held.pop(key, None)
        try:
            os.unlink(str(path))
        except FileNotFoundError:
            pass
