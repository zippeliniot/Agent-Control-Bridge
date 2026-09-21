"""Windows-Benachrichtigung bei Fertigmeldung (BRIDGE-0069).

Erkennung und Ausgabe sind getrennt: ``new_entries`` / ``CompletionWatcher``
sind reine Logik (Notifier injizierbar), ``PowerShellToastNotifier`` ist der
einzige Teil mit Prozessaufruf. Alles hier ist rein lesend - kein Store-Write,
kein Audit, kein Statuswechsel. Fehler der Meldung werden nur nach stderr
geloggt (fail-open).
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Callable, Dict, Iterable, List, Set, Tuple

Notifier = Callable[[str, str], None]

TOAST_TIMEOUT_SECONDS = 10
_MAX_TEXT_LEN = 200

# Konstantes Skript: ID und Titel kommen ausschliesslich ueber Umgebungsvariablen
# (nie in den Befehlsstring eingebettet). CreateTextNode escaped den Text.
_TOAST_SCRIPT = (
    "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
    "ContentType = WindowsRuntime] | Out-Null; "
    "$x = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
    "[Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
    "$t = $x.GetElementsByTagName('text'); "
    "$t.Item(0).AppendChild($x.CreateTextNode($env:ACB_NOTIFY_ID)) | Out-Null; "
    "$t.Item(1).AppendChild($x.CreateTextNode($env:ACB_NOTIFY_TITLE)) | Out-Null; "
    "$n = [Windows.UI.Notifications.ToastNotification]::new($x); "
    "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("
    "'Agent Control Bridge').Show($n)"
)


def new_entries(base_ids: Iterable[str], current: Dict[str, str]) -> List[Tuple[str, str]]:
    """Neu eingetretene Auftraege: in ``current`` (ID -> Titel), nicht in ``base_ids``.

    Rueckgabe sortiert nach ID als Liste von ``(task_id, title)``.
    """
    base = set(base_ids)
    return [(tid, current[tid]) for tid in sorted(current) if tid not in base]


def null_notifier(task_id: str, title: str) -> None:
    """Tut nichts (Standard ohne --notify, Nicht-Windows)."""


class PowerShellToastNotifier:
    """Windows-Toast ueber ``powershell.exe`` (Bordmittel).

    Nur unter Windows aktiv, sonst still (kein Prozessaufruf). Kein
    ``shell=True``, feste Argumentliste, Timeout. Alle Fehler nur nach stderr.
    """

    def __init__(self, runner=subprocess.run, platform: str = sys.platform,
                 timeout: float = TOAST_TIMEOUT_SECONDS, environ=None):
        self._runner = runner
        self._platform = platform
        self._timeout = timeout
        self._environ = environ

    def __call__(self, task_id: str, title: str) -> None:
        if not self._platform.startswith("win"):
            return
        env = dict(os.environ if self._environ is None else self._environ)
        env["ACB_NOTIFY_ID"] = str(task_id)[:_MAX_TEXT_LEN]
        env["ACB_NOTIFY_TITLE"] = str(title)[:_MAX_TEXT_LEN]
        args = ["powershell.exe", "-NoProfile", "-NonInteractive",
                "-Command", _TOAST_SCRIPT]
        try:
            proc = self._runner(args, env=env, timeout=self._timeout,
                                capture_output=True, text=True, check=False)
        except Exception as exc:  # noqa: BLE001 - fail-open: fehlt, Timeout, ...
            print(f"Benachrichtigung fehlgeschlagen: {exc}", file=sys.stderr)
            return
        code = getattr(proc, "returncode", 0)
        if code:
            print(f"Benachrichtigung fehlgeschlagen: powershell.exe Exit-Code {code}",
                  file=sys.stderr)


class CompletionWatcher:
    """Meldet je Zustandseintritt genau einmal (Entprellung ueber Basis-Menge).

    ``snapshot`` liefert ``{task_id: title}`` der Auftraege in
    ``WAITING_FOR_COPY_TO_CONTROL``. Beim Anlegen wird der Bestand als Basis
    gemerkt (Altbestand still); jeder Aufruf gleicht gegen die Menge des
    letzten Abgleichs ab, sodass Verlassen und Wiedereintritt erneut meldet.
    """

    def __init__(self, snapshot: Callable[[], Dict[str, str]], notifier: Notifier):
        self._snapshot = snapshot
        self._notifier = notifier
        self._base: Set[str] = set(snapshot())

    def __call__(self) -> None:
        current = self._snapshot()
        entries = new_entries(self._base, current)
        self._base = set(current)
        for task_id, title in entries:
            try:
                self._notifier(task_id, title)
            except Exception as exc:  # noqa: BLE001 - fail-open
                print(f"Benachrichtigung fehlgeschlagen: {exc}", file=sys.stderr)
