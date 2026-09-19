# BRIDGE-0042 - Baseline- und Grundlagen-Check (Punkte 1,3,4)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0042 |
| project_id | agent-control-bridge |
| Typ / Klasse | T0 / CHORE |
| Rechte | READ_ONLY, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Baseline-Pruefung, nur lesen, muss zuverlaessig sein. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | - |
| Gate | G0 |
| stop_conditions | HEAD_MISMATCH, CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Ausgangslage pruefen und Abweichungen melden. Keine Projektdatei aendern.

## Scope
Nur lesen. Schreiben nur ueber Bridge-CLI (Store).

## Schritte
1. `git remote -v; git branch -vv; git log --oneline -5` - HEAD muss Nachfolger von cbeb7ff sein (`git merge-base --is-ancestor cbeb7ff HEAD`).
2. IDs: hoechster Ordner in tasks/ = BRIDGE-0041; BRIDGE-0043..0066 in tasks/ frei.
3. Vorhanden? docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md und work-packages/BRIDGE-042..066.md.
4. `git grep -il kollisionsschutz -- docs` - Datei 'Kollisionsschutz V2' vorhanden? (erwartet: NEIN)
5. Gates im Konzept zaehlen (erwartet: 6, G0-G5).
6. Befund max. 12 Zeilen in --summary.

## Tests
Keine.

## Akzeptanzkriterien
- [x] HEAD ist Nachfolger von cbeb7ff
- [x] IDs 0043-0066 frei
- [x] Konzept V2 + 25 Pakete vorhanden
- [x] Befund zu Kollisionsschutz V2 gemeldet
- [x] 6 Gates bestaetigt
