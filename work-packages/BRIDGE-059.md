# BRIDGE-0059 - Entscheidung Audit-Strategie

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0059 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / MEDIUM** - Kurze Entscheidung mit Alternativen. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0058 |
| Gate | G2 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Eine Entscheidungsdatei. Keine Implementierung.

## Scope
Neu: docs/concepts/ENTSCHEIDUNG-AUDIT.md (max. 40 Zeilen).

## Schritte
1. Ist-Stand notieren: audit.jsonl 260 Zeilen, ca. 58 KB.
2. Optionen: (A) eine Datei + sicheres Append, (B) Monatsdateien. Default-Empfehlung A; B erst ab 1 MB oder 5000 Zeilen.
3. Konsequenz fuer Lesecode (`last_transition_at`, overview, watcher) je Option 2 Zeilen.
4. Status ENTWURF - Freigabe durch April.

## Tests
Keine.

## Akzeptanzkriterien
- [ ] Entscheidungsdatei mit A/B, Schwellwert, Empfehlung
- [ ] Lesecode-Folgen benannt
