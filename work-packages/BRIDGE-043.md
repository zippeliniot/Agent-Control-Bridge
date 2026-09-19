# BRIDGE-0043 - Entscheidung Push-Modell und Kollisionsschutz-Grundlage (Punkte 2,3)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0043 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / HIGH** - Widerspruechliche Konzepte (Push-Modell) - HIGH ist hier ausdruecklich vorgesehen. |
| Modellwechsel zum Vorgaenger | JA |
| depends_on | BRIDGE-0042 |
| Gate | G1 |
| stop_conditions | CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Genau eine Entscheidungsvorlage schreiben. Keine Implementierung.

## Scope
Neu: docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md (max. 60 Zeilen).

## Schritte
1. Datei mit Kopfzeile `Status: ENTWURF` anlegen.
2. Optionen A (alles bleibt: Executor pusht), B (Draft-Modus nur pro Projekt per Feld `push_mode`), C (sofort Single-Writer) je 3 Zeilen: Folge + Risiko.
3. Empfehlung: B. Uebergangsregel: bis Gate G2 gelten CLAUDE.md-Regeln (GIT_PUSH, sofort pushen) unveraendert; danach nur in Projekten mit `push_mode: draft`.
4. Kollisionsschutz V2: falls nicht im Repo, Mindestspezifikation (max. 15 Zeilen: Single-Writer, Lock, CAS-Ausblick) in dieselbe Datei.
5. Auf Freigabe durch April warten - NICHT selbst auf FREIGEGEBEN setzen.

## Tests
Nur Sichtpruefung der Datei.

## Akzeptanzkriterien
- [x] Datei mit Optionen A/B/C und Empfehlung
- [x] Uebergangsregel bis G2 dokumentiert
- [x] Kollisionsschutz-V2-Behandlung dokumentiert
- [x] Status steht auf ENTWURF (Freigabe durch April)
