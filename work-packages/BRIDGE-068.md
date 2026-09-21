# BRIDGE-0068 - Entscheidung Windows-Benachrichtigung bei Fertigmeldung

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0068 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Teile (alte Nummern) | 0068 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / MEDIUM** - Kurze Entscheidung mit Alternativen. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0063 |
| Gate | keines |
| stop_conditions | CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0068` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag
**Ziel:** Eine Entscheidungsdatei. Keine Implementierung.
**Scope:** Neu: docs/concepts/ENTSCHEIDUNG-BENACHRICHTIGUNG.md (max. 40 Zeilen). Sonst nichts.
1. Ist-Stand notieren: Fertigmeldung heute = Executor pusht result.yaml, Auftrag steht auf WAITING_FOR_COPY_TO_CONTROL, der Board-Klon holt per Auto-Pull (`webui serve`, Standard 30 s). April bemerkt es nur durch Hinsehen.
2. Funktion festhalten: Windows-Benachrichtigung auf der Maschine mit der Web-UI, wenn ein Auftrag neu auf WAITING_FOR_COPY_TO_CONTROL steht. Inhalt nur Auftrags-ID und Titel, kein Ergebnisinhalt.
3. Optionen fuer den Ort: (A) Hook im Auto-Pull-Thread von `webui serve`, (B) `board --watch`. Je 2 Zeilen: wo es heute laeuft, was fehlt, Grenze (laeuft nur solange das Fenster offen ist).
4. Kanal: Windows-Toast ueber `powershell.exe` ohne Zusatzpakete, kein Netz, keine Mail. Aktivierung per Opt-in-Flag. Nicht-Windows: still ohne Meldung.
5. Regeln festhalten: rein lesend (kein Store-Write, kein Statuswechsel, G2 unberuehrt); fail-open (Fehler der Meldung bricht nichts ab); Entprellung (je Zustandseintritt einmal, Neustart meldet keinen Altbestand); Notifier injizierbar (Linux-Tests ohne Windows).
6. Empfehlung A oder B, dazu Schnitt des Folgeauftrags BRIDGE-0069 (T2, Sonnet 5 / MEDIUM) in max. 3 Zeilen.
7. Status ENTWURF - Freigabe durch April.
**Tests:** Keine.
- [ ] Entscheidungsdatei mit A/B, Regeln, Empfehlung
- [ ] Schnitt von BRIDGE-0069 benannt