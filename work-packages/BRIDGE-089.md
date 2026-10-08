# BRIDGE-0089 - Nachbesserung BRIDGE-0088: Ist/Soll-Korrektur, Herkunftsnachweis, V2-Praezisierung

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0089 |
| project_id | agent-control-bridge |
| Typ / Klasse | ARCHITECTURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Inhaltliche Korrektur an bestehenden Konzept-/Entscheidungsdokumenten mit Entscheidungscharakter (wie BRIDGE-0088/0073), kein Widerspruchs-/Sicherheitsfall, kein Code-Risiko. |
| Modellwechsel zum Vorgaenger | NEIN (Vorgaenger BRIDGE-0088: Claude Sonnet 5 / MEDIUM, ARCHITECTURE) |
| depends_on | BRIDGE-0088 (Status WAITING_FOR_COPY_TO_CONTROL zum Zeitpunkt der Erstellung dieses Auftrags - BRIDGE-0088 wird dadurch inhaltlich **nicht** erneut aufgerollt, nur ergaenzt/korrigiert) |
| Gate | keines (reine Dokumentkorrektur, kein Code, kein G2/G3/G4-Scope beruehrt) |
| stop_conditions | CONCEPT_CONFLICT |
| Multi-Agent | NEIN |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0089` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: Claude Sonnet 5 / DENKSTUFE: MEDIUM`. Abweichung von der Tabelle = STOPP.

## Anlass

BRIDGE-0088 (Status WAITING_FOR_COPY_TO_CONTROL, `tasks/BRIDGE-0088/task.yaml` task_version 7,
Head `815ec26`) wurde bereits in Claude Code ausgefuehrt und gepusht, **bevor** eine im
Steuerchat nachtraeglich erarbeitete Korrekturrunde (Pruefung externer Anmerkungen zu BRIDGE-0088)
in die beiden Dokumente eingearbeitet werden konnte. Die im Repo liegenden Fassungen von
`docs/concepts/RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` und
`docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` entsprechen damit dem
**unkorrigierten** Entwurfsstand. Dieser Auftrag holt die Korrektur nach, ohne BRIDGE-0088 selbst
zu veraendern (Auftraege sind unveraenderlich, CLAUDE.md: "es gibt bewusst kein `task edit`" -
Korrektur = naechste freie `BRIDGE-00NN`).

Kein neuer Scope, keine neue fachliche Frage - ausschliesslich Praezisierung der in BRIDGE-0088
bereits angelegten zwei Dokumente.

## Auftrag

**Ziel:** Fehlerkorrektur an genau den zwei bestehenden Dateien aus BRIDGE-0088. Keine neue Datei,
keine Implementierung, keine Schema-Aenderung, keine Entscheidung (V2 bleibt ENTWURF).

**Scope:** Nur `docs/concepts/RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` und
`docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` bearbeiten. Sonst nichts. Kein
Code, kein `schemas/`-Eintrag, keine Aenderung an `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md`
(V1 bleibt unveraendert).

### Teil A - `RAG-RETRIEVAL-PIPELINE-SPEZIFIKATION.md` korrigieren

1. Zeile zu `structured_coverage`: "- der Soll-Zustand." ersetzen durch "- der jeweils aktuelle
   Ist-Zustand (kein fester Zielwert/Soll definiert)." `structured_coverage` beschreibt
   nachgewiesene tatsaechliche Abdeckung, keinen Zielwert.
2. Zeile zu `migration_status`: "die Luecke zwischen Soll (`structured_coverage`) und Ist."
   ersetzen durch "die Luecke zwischen diesem Ist-Zustand und vollstaendiger Konsolidierung (kein
   fester Soll-Wert definiert)."
3. Zeile zu `context_sources_used`, Abgrenzungssatz: "structured_coverage = Soll je Projekt
   (zeitlos), migration_status = Luecke im Soll (zeitlos)" ersetzen durch "structured_coverage =
   Ist-Stand je Projekt (zeitlos, zum jeweiligen Abfragezeitpunkt), migration_status = Luecke
   zwischen diesem Ist-Stand und vollstaendiger Konsolidierung (zeitlos)".
4. Zeile zu `Herkunftsnachweis`: "Jede injizierte Information traegt eine nachvollziehbare
   Quellenangabe (Datei + Revision, oder Steuerchat-Session-Verweis)." ersetzen durch: jede
   injizierte Information traegt Datei + Revision (bzw. definierter Snapshot) **und** konkrete
   Fundstelle; ein reiner Steuerchat-Session-Verweis reicht allein **nicht**, da Steuerchat-
   Sitzungen keine dauerhaft referenzierbare, versionierte Quelle sind - jede Aussage muss auf
   eine dauerhaft zugaengliche Quelle zurueckfuehrbar sein.

### Teil B - `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` praezisieren

Weiterhin ENTWURF, weiterhin keine Entscheidung - nur die drei inhaltlichen Luecken aus der
Pruefrunde schliessen:

1. §3a: Statt nur "Annahme/Ablösung" vier getrennte Ereignisse vorsehen: **Annahme, Ablehnung,
   Widerruf, Ablösung**. Zusaetzlich: `supersedes` kann **teilweise** geltend sein (eine neue
   Entscheidung loest nur einen Teilaspekt der alten ab, der Rest bleibt gueltig) - das Ereignis
   braucht dafuer einen Geltungsbereich, nicht nur einen Verweis auf die gesamte alte Entscheidung.
2. §3b: `origin_task_id` ausdruecklich als **optional** markieren - eine Entscheidung kann einem
   Auftrag vorausgehen oder unabhaengig davon entstehen.
3. §3c: `affects`/`implemented_by`/`verified_by` nicht auf Code beschraenken - "betroffene
   Einheit" kann ein Fachkonzept, Kapitel, eine Komponente oder Schnittstelle sein, nicht nur eine
   Code-Datei; Revisionsbindung (Repo + Commit/Snapshot) gilt fuer beide Arten von Bezug gleich.

Kein `schemas/decision.schema.yaml`, keine Aenderung an `task.schema.yaml` - das bleibt laut V2
§5 eine eigene, hier nicht mitentschiedene Frage.

- [x] Alle vier Teil-A-Korrekturen angewendet, keine weitere inhaltliche Aenderung an Teil A
- [x] Alle drei Teil-B-Praezisierungen angewendet, Status-Zeile "ENTWURF - ENTSCHEIDUNG AUSSTEHEND"
      unveraendert, keine Entscheidung getroffen
- [x] `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md` (V1) unangetastet (`git diff` zeigt keine
      Aenderung)
- [x] Kein neues Schema, keine `additionalProperties`-Aenderung

## Abschluss

1. Volle Suite EINMAL, nur die letzten 3 Zeilen zeigen (keine Code-Aenderung erwartet, Suite dient
   nur als Regressions-Nachweis).
2. `git status` sauber nach dem Commit (working tree clean - die zwei bearbeiteten Dateien sind
   der erwartete, gewollte Diff).
- [x] Volle Suite gruen, Testanzahl identisch zum Stand nach BRIDGE-0088 (laut dessen Ergebnis:
      575) - keine Zahl vorab fixieren, massgeblich ist "kein Test entfernt, keiner neu, keiner rot"
- [x] `git diff --stat` zeigt ausschliesslich die beiden genannten Dokumente (plus `audit.jsonl`)
