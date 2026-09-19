# BRIDGE-0059 - Entscheidung Audit-Strategie

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0059 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Teile (alte Nummern) | 0059 |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / MEDIUM** - Kurze Entscheidung mit Alternativen. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0057 |
| Gate | G2 |
| stop_conditions | CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0059` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag
**Ziel:** Eine Entscheidungsdatei. Keine Implementierung.
**Scope:** Neu: docs/concepts/ENTSCHEIDUNG-AUDIT.md (max. 40 Zeilen).
1. Ist-Stand notieren: audit.jsonl 260 Zeilen, ca. 58 KB.
2. Optionen: (A) eine Datei + sicheres Append, (B) Monatsdateien. Default-Empfehlung A; B erst ab 1 MB oder 5000 Zeilen.
3. Konsequenz fuer Lesecode (`last_transition_at`, overview, watcher) je Option 2 Zeilen.
4. Status ENTWURF - Freigabe durch April.
**Tests:** Keine.
- [ ] Entscheidungsdatei mit A/B, Schwellwert, Empfehlung
- [ ] Lesecode-Folgen benannt
