# RAG-Infrastruktur-Voraussetzungen (manuell herzustellen)

Stand BRIDGE-0084. ACB erkennt bei jedem `run start` eines Auftrags mit `rag_enabled: true`
automatisch, was fehlt (`src/bridge/rag_prereqs.py`), installiert aber nichts selbst
unbeaufsichtigt (CLAUDE.md-Grundsatz "fail-closed: anhalten und melden, nicht selbst
installieren", hier auf RAG uebertragen). Das Beheben fehlender Voraussetzungen laeuft ueber
`scripts/rag-setup.ps1` - und zwar **nur nach einer expliziten Bestaetigung durch den
Menschen** (BRIDGE-0084, "Skript bereit, Klick bestaetigt Installation"), niemals automatisch.

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

**Wichtig - Modell-Speicherort (BRIDGE-0085, Lehre aus HAM11 07.10.2026):** Ollama legt
heruntergeladene Modelle standardmaessig unter `%USERPROFILE%\.ollama\models` ab - das liegt
auf `C:` und kann dort schnell eng werden. Ollama liest dafuer die Umgebungsvariable
`OLLAMA_MODELS` und nutzt stattdessen deren Pfad, wenn gesetzt:

```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "E:\_DEV\ollama-models", "User")
```

Danach den Ollama-Dienst neu starten (beenden + erneut starten, oder Rechner neu starten),
damit die Variable greift. `scripts/rag-setup.ps1` setzt das seit BRIDGE-0085 automatisch auf
`E:\_DEV\ollama-models`, **bevor** es eine fehlende Ollama-Installation nachzieht - aber nur,
wenn die Variable vorher leer war; ein bestehender bewusster Wert wird nie ueberschrieben. Bei
einer bereits laufenden Installation (wie auf HAM11) muss das nachtraeglich manuell gesetzt
und der Dienst neu gestartet werden; vorhandene Modelle unter dem alten Pfad entweder
verschieben oder per `ollama pull` am neuen Ort neu laden - siehe auch
`scripts/rag-ollama-inventory.ps1` (Abschnitt 4) zum Auffinden und Aufraeumen doppelter
Installationen/Modellablagen.

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

- Einrichten: manuell (siehe oben) **oder** per `scripts/rag-setup.ps1` (siehe Abschnitt 4) -
  beides fuehrt zum selben Ergebnis, das Skript fragt vor dem `git clone` ausdruecklich nach.
- Git LFS muss installiert sein (`git lfs install`, einmalig je Maschine) - sonst bleiben die
  grossen Indexdateien als Platzhalterzeiger liegen.
- Danach synchronisiert ACB diesen Klon automatisch bei jedem `run start` eines
  RAG-aktivierten Auftrags, wenn ein Maschinenwechsel erkannt wird (`git pull` + `git lfs
  pull`, `src/bridge/gitops.py::rag_index_sync`, fail-soft) - das **Anlegen** des Klons selbst
  bleibt aber immer ein bestaetigter Erstschritt (manuell oder per Skript).

## 4. Setup-Skript `scripts/rag-setup.ps1` (BRIDGE-0084)

Auf HAM11/DES11 ausfuehren:

```
pwsh scripts\rag-setup.ps1
```

Ablauf: das Skript prueft dieselben drei Signale wie `rag_prereqs.check` (Ollama erreichbar,
Modell vorhanden, Index-Klon vorhanden), zeigt eine Statusuebersicht, listet bei fehlenden
Komponenten **vor jeder Aktion** genau auf, was es tun wuerde, und fragt dann ausdruecklich
nach Bestaetigung ("ja"/"nein"). Nur bei bestaetigter Eingabe installiert es die fehlenden
Komponenten (Ollama, `ollama pull nomic-embed-text`, `git clone` + `git lfs pull` fuer
`rag-index`) - jeder Schritt einzeln geprueft, ein Fehlschlag bricht sofort ab. Es gibt
bewusst keinen Parameter, der die Bestaetigung ueberspringt.

## Was ACB automatisch tut vs. was manuell bleibt

| Schritt | Automatisch durch ACB | Manuell / bestaetigt |
|---|---|---|
| Ollama installieren | nein | ja - manuell oder per `rag-setup.ps1` (bestaetigt) |
| `nomic-embed-text` laden | nein | ja - manuell oder per `rag-setup.ps1` (bestaetigt) |
| `rag-index`-Klon anlegen | nein | ja - manuell oder per `rag-setup.ps1` (bestaetigt) |
| `rag-index` bei Maschinenwechsel aktualisieren | ja (`git pull` + `git lfs pull`) | - |
| Fehlende Voraussetzung erkennen und melden | ja (`run start`, stderr-Hinweis) | - |
| Fehlende Voraussetzung beheben | nein (erfordert Bestaetigung) | ja, per `rag-setup.ps1` |

## Fehlermeldung in der Praxis

Fehlt etwas, gibt `bridge run start` eine Zeile auf stderr aus, z. B.:

```
RAG-Infrastruktur unvollstaendig: fehlt ollama, embed_model:nomic-embed-text, index_clone
(siehe docs/concepts/RAG-INFRASTRUKTUR-VORAUSSETZUNGEN.md)
```

Der Lauf selbst wird dadurch **nicht** blockiert (fail-soft, gleiches Prinzip wie der
RAG-Index-Sync aus BRIDGE-0082) - die Meldung ist ein Hinweis, keine Fehlerabbruch.
