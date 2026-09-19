"""Fehlercodes als SSOT (BRIDGE-0047 Teil C).

Liest ``schemas/error-codes.yaml``. Alle Codes mappen auf den bestehenden
Zustand BLOCKED. Fail-closed: fehlende/ungueltige Datei -> ``ErrorCodeError``.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from bridge.store import StoreError

_FILE = "error-codes.yaml"
_cache: dict[str, dict] = {}


class ErrorCodeError(StoreError):
    """Fehlercode-Datei fehlt oder ist ungueltig."""


def load_error_codes(schema_dir) -> dict[str, dict]:
    """Laedt ``error-codes.yaml`` und liefert ``{code: {description, state}}``."""
    path = Path(schema_dir) / _FILE
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ErrorCodeError(f"{path}: nicht lesbar: {exc}") from exc
    codes = doc.get("codes") if isinstance(doc, dict) else None
    if not isinstance(codes, dict) or not codes:
        raise ErrorCodeError(f"{path}: 'codes' fehlt oder ist leer")
    for code, entry in codes.items():
        if (not isinstance(entry, dict) or not entry.get("description")
                or entry.get("state") != "BLOCKED"):
            raise ErrorCodeError(f"{path}: Code {code} ohne description/state BLOCKED")
    _cache.clear()
    _cache.update(codes)
    return dict(codes)


def is_known(code, schema_dir=None) -> bool:
    """True, wenn ``code`` ein bekannter Fehlercode ist.

    Ohne ``schema_dir`` wird die zuletzt mit ``load_error_codes`` geladene
    Tabelle genutzt (leer -> False, fail-closed).
    """
    codes = load_error_codes(schema_dir) if schema_dir is not None else _cache
    return isinstance(code, str) and code in codes
