# ACB - Umsetzungskonzept tokenoptimierte Arbeitsauftraege V2

**Status:** verbindlich nach Freigabe BRIDGE-0043 | **Stand:** 2026-09-19 | **Basis-HEAD:** cbeb7ff
Ersetzt V1 (`ACB_UMSETZUNGSKONZEPT_TOKENOPTIMIERTE_ARBEITSAUFTRAEGE_V1.md`). Aenderungen gegenueber V1: siehe §6.

## 1. Grundsaetze (V1 §1-2, unveraendert gueltig)
Ein Auftrag = ein Ziel. Read-only zuerst. `allowed_paths`/`forbidden_actions`. Keine Wiederholung (Pfad/SHA statt Kopie).
Unklarheit = BLOCKED mit Code. Modell folgt dem Risiko. Bridge antwortet kurz, prueft nie kurz.

## 2. Nummernraum (Punkt 1)
Repo hat BRIDGE-0001..0041 vergeben. Neue Kette = **BRIDGE-0042..0066**, Format 4-stellig, WP-Dateinamen 3-stellig (`BRIDGE-042.md`, damit die `--commit`-Whitelist greift).
V1-Nummer -> neu: 001->0042, 002->0043, 003..022 -> 0047..0066 (+44). Neu dazu: 0044 (Namen), 0045 (Topologie), 0046 (Housekeeping).

## 3. Standardregeln (gelten fuer JEDEN Auftrag)
- **R0 MODELL-GATE:** Vor Umsetzung Modell + Denkstufe laut Paket setzen. Erste Antwortzeile: `MODELL: .. / DENKSTUFE: ..`. Abweichung = STOPP.
- **R1** Kontext nur: dieses Konzept §3 + das eigene WP + im WP genannte Dateien. Kein Repo-Scan, keine Historie.
- **R2** Aenderungen nur per Einzel-Edit (`str_replace`). Nie ganze Dateien ausgeben oder neu schreiben, ausser die Datei ist neu.
- **R3** Tests: erst gezielt, dann volle Suite EINMAL. Ausgabe nur die letzten 3 Zeilen. Bei FAIL nur die betroffenen Zeilen.
- **R4** Nur `allowed_paths` des WP. Historische Dateien (tasks/*, results/*, fremde work-packages/*, docs/handover/CCB-*) nie aendern.
- **R5** Zustandsaenderungen nur per Bridge-CLI. Kein `git add -A`, nie `--force`.
- **R6** `run finish` immer mit `--commit` und `--summary` (max. 3 Saetze, konkret). Haken im eigenen WP setzen.
- **R7** Push: bis Gate G2 gilt CLAUDE.md (GIT_PUSH, sofort pushen). Danach in `push_mode: draft`-Projekten nur Drafts.
- **R8** Unklar = BLOCKED + Fehlercode + ein Beweis. Nicht weiterarbeiten.
- Handover im Chat max. 12 Zeilen: `id status type model reasoning head result tests findings next`.

## 4. Auftragstypen und Modellmatrix
T0 Bestandspruefung (lesen) | T1 Entscheidung | T2 Einzelimplementierung | T3 Test | T4 Integration | T5 Abschluss.
| Typ | Modell | Stufe |
|---|---|---|
| T0 einfach | Haiku 4.5 | LOW |
| T0 Sicherheit/Baseline | Sonnet 5 | MEDIUM |
| T1 Entscheidung | Opus 5 | MEDIUM (HIGH nur bei Widerspruch/Sicherheit) |
| T2 lokal / additiv | Sonnet 5 | LOW-MEDIUM |
| T2 sicherheitsrelevant | Sonnet 5 | MEDIUM |
| T3 Tests | Sonnet 5 | LOW |
| T4 Import/Push | Sonnet 5 + Freigabe April | MEDIUM |
| T5 Abschluss | Opus 5 | MEDIUM-HIGH |
Steuerchat setzt Modell/Stufe im WP UND in der Staging-YAML (`model`, `reasoning_level`). Modellwechsel nur ueber Result-Datei/SHA, nie ueber Chatverlauf.

## 5. Gates (sechs: G0-G5)
- **G0** Bestandsklarheit: kein Code, bis BRIDGE-0042 PASS.
- **G1** Architektur: kein Code, bis BRIDGE-0043 `Status: FREIGEGEBEN` und BRIDGE-0047..0050 fertig.
- **G2** Stufe A: gilt erst nach PASS BRIDGE-0055 + Eintrag `G2: IN KRAFT` durch April. Danach kein Executor-Push und kein Executor-Write unter tasks/, results/, audit/ (nur in `push_mode: draft`).
- **G3** Stufe B: `task_version`/CAS/Claim erst nach ausdruecklicher Freigabe im Chat.
- **G4** Parallelitaet: kein Parallelbetrieb ohne Ressourcenregel (BRIDGE-0063) + Tests (BRIDGE-0064).
- **G5** Dorfschaft: keine Dorfschaft-Aenderung. Pilot bleibt read-only; WSL-Pfad muss von April bestaetigt sein.

## 6. Korrekturen gegenueber V1 (Punkte 1-7)
1. Nummernraum: 0042..0066 statt 001..022 (§2).
2. Push-Modell: Uebergangsregel R7, Entscheidung BRIDGE-0043, Feld `push_mode` (BRIDGE-0047).
3. Kollisionsschutz V2 nicht im Repo: BRIDGE-0042 meldet, BRIDGE-0043 legt Mindestspezifikation fest.
4. Zaehlung: **sechs** Gates (G0-G5). Kein "AP-D1": die Ressourcenregel ist BRIDGE-0063.
5. Namensreste: BRIDGE-0044.
6. Topologie claude -> dev: BRIDGE-0045.
7. Haken/Handover: BRIDGE-0046.
V1-Aufgaben "Schema definieren" (003-006) sind Deltas: task/result/state-model existieren bereits.

## 7. Resume
Usage-Limit/Toolfehler: keine neue BRIDGE-ID, Auftrag unveraendert, `run resume`, nur offene Haken uebergeben.

## 8. Definition of Done
Modell-Gate erfuellt, Scope eingehalten, Tests real gezaehlt, Draft/Result valide, Haken gesetzt, gepusht (R7), Footer + 12-Zeilen-Handover.

## 9. Paketliste
| ID | Typ | Modell | Stufe | Gate | Titel |
|---|---|---|---|---|---|
| BRIDGE-0042 | T0 | Sonnet 5 | MEDIUM | G0 | Baseline- und Grundlagen-Check (Punkte 1,3,4) |
| BRIDGE-0043 | T1 | Opus 5 | HIGH | G1 | Entscheidung Push-Modell und Kollisionsschutz-Grundlage (Punkte 2,3) |
| BRIDGE-0044 | T2 | Sonnet 5 | LOW | G1 | Namensreste beseitigen (Punkt 5) |
| BRIDGE-0045 | T2 | Sonnet 5 | MEDIUM | G1 | Topologie angleichen: claude -> dev (Punkt 6) |
| BRIDGE-0046 | T2 | Sonnet 5 | LOW | G1 | Housekeeping: Haken und fehlende Handover (Punkt 7) |
| BRIDGE-0047 | T2 | Sonnet 5 | MEDIUM | G1 | Profilfeld push_mode |
| BRIDGE-0048 | T2 | Sonnet 5 | LOW | G1 | Task-Schema: task_type, allowed_paths, forbidden_actions, stop_conditions |
| BRIDGE-0049 | T2 | Sonnet 5 | MEDIUM | G1 | Draft-Schema draft-a-1 |
| BRIDGE-0050 | T2 | Sonnet 5 | LOW | G1 | Fehlercodes als SSOT |
| BRIDGE-0051 | T2 | Sonnet 5 | MEDIUM | G1 | Draft-Ablage im Store |
| BRIDGE-0052 | T2 | Sonnet 5 | LOW | G1 | CLI: task brief (tokenarmer Kurzauftrag) |
| BRIDGE-0053 | T2 | Sonnet 5 | MEDIUM | G1 | CLI: draft write (Executor-Seite) |
| BRIDGE-0054 | T4 | Sonnet 5 | MEDIUM | G1 | CLI: draft import (Board-Seite) mit --dry-run |
| BRIDGE-0055 | T3 | Sonnet 5 | LOW | G2 | Stufe-A-Abnahmetest |
| BRIDGE-0056 | T2 | Sonnet 5 | LOW | G2 | Executor-Regeln auf Draft-Modus pruefen |
| BRIDGE-0057 | T0 | Sonnet 5 | MEDIUM | G2 | Zweischichtige Push-Sperre: Nachweis |
| BRIDGE-0058 | T2 | Sonnet 5 | MEDIUM | G2 | Atomare Store-Writes |
| BRIDGE-0059 | T1 | Opus 5 | MEDIUM | G2 | Entscheidung Audit-Strategie |
| BRIDGE-0060 | T2 | Sonnet 5 | MEDIUM | G2 | Writer-Lock und sicheres Audit-Append |
| BRIDGE-0061 | T2 | Sonnet 5 | MEDIUM | G3 | Version und CAS (Stufe B) |
| BRIDGE-0062 | T2 | Sonnet 5 | MEDIUM | G3 | Claim/Lease-API |
| BRIDGE-0063 | T1 | Opus 5 | MEDIUM | G4 | Ressourcenregel (repository, remote, branch) |
| BRIDGE-0064 | T3 | Sonnet 5 | LOW | G4 | Parallelitaets- und Ausfalltests |
| BRIDGE-0065 | T2 | Sonnet 5 | MEDIUM | G5 | Dorfschaft: read-only Profil und Pilot-Checkliste |
| BRIDGE-0066 | T3 | Codex-Modell (April tragen ein) | LOW | G5 | Dorfschaft Read-only-Pilot |
Reihenfolge strikt sequentiell (ein Auftrag zur Zeit im Praefix BRIDGE).
