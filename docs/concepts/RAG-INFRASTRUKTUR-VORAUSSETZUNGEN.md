# RAG-Infrastruktur-Voraussetzungen (manuell herzustellen)

Stand BRIDGE-0083. Reine Nachschlage-Beschreibung, **kein** Installationsskript - ACB
erkennt nur, was fehlt (`src/bridge/rag_prereqs.py`, aufgerufen bei jedem `run start` eines
Auftrags mit `rag_enabled: true`), installiert aber nichts selbst (CLAUDE.md-Grundsatz
"fail-closed: anhalten und melden, nicht selbst installieren", hier auf RAG uebertragen). Ein
Mensch-bestaetigtes Installationsskript ("Skript bereit, Klick bestaetigt Installation") ist
BRIDGE-0084 und noch nicht gebaut.

Betroffen sind die Maschinen, auf denen ein Auftrag mit aktiviertem `rag_enabled`
(`projects/<id>/project.yaml`) tatsaechlich laeuft - heute potenziell `HAM11` und `DES11`
(siehe `docs/architecture/machines.md`).

## 1. Ollama-Dienst

RAG braucht einen lokal laufenden Ollama-Dienst, erreichbar unter `http://localhost:11434`
(Standard-Port, von `rag_prereqs.check()` per `GET /api/tags` geprueft).

- Installation: offizieller Ollama-Installer fuer Windows
  (<https://ollama.com/download/windows>), manuell herunterladen und ausfuehren - kein
  automatischer Download durch ACB oder Claude Code.
- Nach Installation startet Ollama als Hintergrunddienst automatisch; Erreichbarkeit pruefen:
  `curl http://localhost:11434/api/tags` sollte ein JSON-Objekt mit `models` liefern (ggf.
  leere Liste, wenn noch kein Modell geladen ist).

## 2. Embedding-Modell `nomic-embed-text`

RAG nutzt `nomic-embed-text` fuer die Vektorisierung (Entscheidung aus dem RAG-Konzept, siehe
Projektuebersicht). `rag_prereqs.check()` prueft, ob ein Modellname `nomic-embed-text` oder
`nomic-embed-text:<tag>` in der Ollama-Modellliste auftaucht.

- Laden: `ollama pull nomic-embed-text` in einer Windows-Eingabeaufforderung/PowerShell -
  manueller Befehl, kein automatischer Pull durch ACB.
- Pruefen: `ollama list` muss `nomic-embed-text` auflisten.

## 3. Lokaler Klon `rag-index`

Der Vektorindex selbst liegt im privaten Repository `zippeliniot/acb-rag-index` (Git LFS) und
wird als fuenfter Geschwisterklon neben `board`/`dev`/`claude`/`codex` erwartet (BRIDGE-0083,
Korrektur der urspruenglichen BRIDGE-0082-Annahme) - siehe `docs/architecture/machines.md`:

```
E:\_DEV\Agent-Control-Bridge\rag-index
```

- Einrichten (einmalig, manuell):
  ```
  cd E:\_DEV\Agent-Control-Bridge
  git clone https://github.com/zippeliniot/acb-rag-index.git rag-index
  cd rag-index
  git lfs pull
  ```
- Git LFS muss installiert sein (`git lfs install`, einmalig je Maschine) - sonst bleiben die
  grossen Indexdateien als Platzhalterzeiger liegen.
- Danach synchronisiert ACB diesen Klon automatisch bei jedem `run start` eines
  RAG-aktivierten Auftrags, wenn ein Maschinenwechsel erkannt wird (`git pull` + `git lfs
  pull`, `src/bridge/gitops.py::rag_index_sync`, fail-soft) - das **Anlegen** des Klons selbst
  bleibt aber immer ein manueller Erststeep.

## Was ACB automatisch tut vs. was manuell bleibt

| Schritt | Automatisch durch ACB | Manuell |
|---|---|---|
| Ollama installieren | nein | ja (einmalig je Maschine) |
| `nomic-embed-text` laden | nein | ja (einmalig je Maschine) |
| `rag-index`-Klon anlegen | nein | ja (einmalig je Maschine) |
| `rag-index` bei Maschinenwechsel aktualisieren | ja (`git pull` + `git lfs pull`) | - |
| Fehlende Voraussetzung erkennen und melden | ja (`run start`, stderr-Hinweis) | - |
| Fehlende Voraussetzung beheben | nein (reserviert fuer BRIDGE-0084) | ja, bis BRIDGE-0084 |

## Fehlermeldung in der Praxis

Fehlt etwas, gibt `bridge run start` eine Zeile auf stderr aus, z. B.:

```
RAG-Infrastruktur unvollstaendig: fehlt ollama, embed_model:nomic-embed-text, index_clone
(siehe docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md)
```

Der Lauf selbst wird dadurch **nicht** blockiert (fail-soft, gleiches Prinzip wie der
RAG-Index-Sync aus BRIDGE-0082) - die Meldung ist ein Hinweis, keine Fehlerabbruch.
