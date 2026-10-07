"""RAG-Infrastruktur-Erkennung (BRIDGE-0083).

Reine Erkennung, ob die lokalen Voraussetzungen fuer RAG (Ollama-Dienst,
Embedding-Modell, Index-Klon) auf der aktuellen Maschine vorhanden sind.

Sicherheitsleitplanke (verbindlich, CLAUDE.md-Grundsatz "fail-closed: anhalten
und melden, nicht selbst installieren" - hier auf RAG uebertragen): dieses
Modul installiert, laedt oder veraendert NICHTS. Es meldet nur, was fehlt.
Die eigentliche Installation (Mensch-bestaetigter Skript-Lauf) ist
ausdruecklich BRIDGE-0084, nicht Teil dieses Moduls.

Fail-soft, zwingend: ``check()`` wirft nie - jeder Fehler (kein Ollama
erreichbar, Timeout, ungueltige Antwort, fehlender Index-Klon) landet als
Eintrag in ``missing``, niemals als Exception. Gleiches Muster wie
``gitops.git_pull``/``rag_index_sync``.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

_TIMEOUT_SECONDS = 3


def _ollama_tags(ollama_url: str) -> list[str] | None:
    """Modellnamen aus ``GET {ollama_url}/api/tags`` oder ``None`` bei
    jedem Fehler (Verbindung, Timeout, ungueltiges JSON) - nie werfen."""
    try:
        with urllib.request.urlopen(
            f"{ollama_url.rstrip('/')}/api/tags", timeout=_TIMEOUT_SECONDS
        ) as resp:
            doc = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    models = doc.get("models") if isinstance(doc, dict) else None
    if not isinstance(models, list):
        return None
    names = []
    for entry in models:
        if isinstance(entry, dict) and isinstance(entry.get("name"), str):
            names.append(entry["name"])
    return names


def check(index_path, *, ollama_url: str = "http://localhost:11434",
          embed_model: str = "nomic-embed-text") -> dict:
    """Prueft Ollama-Erreichbarkeit, Embedding-Modell und Index-Klon.

    Reine Erkennung, kein Installationsversuch, keine Seiteneffekte.

    Rueckgabe:
        ``{"ollama_reachable": bool, "embed_model_present": bool,
          "index_clone_exists": bool, "missing": list[str], "all_ok": bool}``
    """
    tags = _ollama_tags(ollama_url)
    ollama_reachable = tags is not None

    embed_model_present = False
    if ollama_reachable:
        embed_model_present = any(
            name == embed_model or name.startswith(f"{embed_model}:")
            for name in tags
        )

    path = Path(index_path)
    index_clone_exists = path.is_dir() and (path / ".git").exists()

    missing = []
    if not ollama_reachable:
        missing.append("ollama")
    if not embed_model_present:
        missing.append(f"embed_model:{embed_model}")
    if not index_clone_exists:
        missing.append("index_clone")

    return {
        "ollama_reachable": ollama_reachable,
        "embed_model_present": embed_model_present,
        "index_clone_exists": index_clone_exists,
        "missing": missing,
        "all_ok": not missing,
    }
