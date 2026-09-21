# ACB - Umsetzungskonzept tokenoptimierte Arbeitsauftraege V2.1

**Status:** verbindlich (Push-Modell freigegeben BRIDGE-0043) | **Stand:** 2026-09-19 | **Basis:** V2 + Buendelung
Ersetzt V1 und V2. Aenderungen: §6.

## 1. Grundsaetze
Ein Auftrag = ein Bereich. Read-only zuerst. Scope-Pfade. Keine Wiederholung (Pfad/SHA statt Kopie).
Unklarheit = BLOCKED mit Code. Modell folgt dem Risiko. Bridge antwortet kurz, prueft nie kurz.

## 2. Nummernraum und Buendel
Repo hat BRIDGE-0001..0045 vergeben (0042-0045 erledigt). Format 4-stellig, WP-Dateinamen 3-stellig (`BRIDGE-047.md`).
Ab 0046 werden verwandte Teilpakete zu **Buendeln** zusammengefasst; das Buendel traegt die Nummer des ersten passenden Teils.
Aufgegangene Nummern (kein eigener Auftrag): 0048, 0050, 0051, 0052, 0054, 0056, 0058, 0062, 0064.
- BRIDGE-0047 = 0047, 0048, 0050
- BRIDGE-0049 = 0049, 0051, 0052
- BRIDGE-0053 = 0053, 0054
- BRIDGE-0055 = 0055, 0056
- BRIDGE-0060 = 0058, 0060
- BRIDGE-0061 = 0061, 0062
- BRIDGE-0063 = 0063, 0064
Regeln fuer Buendel: gleiches Modell + gleiche Stufe (hoechste Teilstufe), gleicher Bereich, direkt aufeinanderfolgend, nie ueber ein Gate hinweg, Entscheidungen mit Freigabe bleiben einzeln. Pro Teil eigener Commit, Push und Haken.

## 3. Standardregeln (jeder Auftrag)
- **R0 MODELL-GATE:** Modell + Denkstufe laut WP setzen (`/model`). Erste Antwortzeile `MODELL: .. / DENKSTUFE: ..`. Abweichung = STOPP.
- **R1** Kontext nur: dieses §3 + eigenes WP + im WP genannte Dateien. Kein Repo-Scan.
- **R2** Aenderungen nur per Einzel-Edit. Nie ganze Dateien ausgeben, ausser die Datei ist neu.
- **R3** Tests je Teil gezielt, volle Suite EINMAL am Ende, nur die letzten 3 Zeilen.
- **R4** Nur Scope des WP. Historische Dateien (tasks/*, results/*, fremde work-packages/*, docs/handover/CCB-*) nie aendern.
- **R5** Zustandsaenderungen nur per Bridge-CLI. Kein `git add -A`, nie `--force`.
- **R6** Arbeit VOR `run finish` committen und pushen (Status sauber). Danach `run finish --commit --summary` (max. 3 Saetze).
- **R7** Push: bis Gate G2 gilt CLAUDE.md (GIT_PUSH, sofort pushen). Danach in `push_mode: draft`-Projekten nur Drafts.
- **R8** Unklar = BLOCKED + Fehlercode + ein Beweis. Nicht weiterarbeiten.
- **R9** Kein Handover-Text. Claude Code gibt Footer + max. 3 Zeilen aus; der Steuerchat liest Ergebnis, Diff und Audit selbst aus dem Repo.

## 3a. Ablauf pro Auftrag
Einzige Quelle: `.claude/commands/acb-auftrag.md`. Aufruf: `/acb-auftrag BRIDGE-00xx` (Fallback ohne Command: "Fuehre Auftrag BRIDGE-00xx aus: lies .claude/commands/acb-auftrag.md und befolge es wortgenau").
Wiederaufnahme ist eingebaut (vorhandener Auftrag/Status wird erkannt, nichts doppelt angelegt).

## 4. Modellmatrix
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
Buendel: Modell/Stufe = hoechste Teilstufe. Wird in WP UND Staging-YAML (`model`, `reasoning_level`) gesetzt.

## 5. Gates (sechs: G0-G5)
- **G0** Bestandsklarheit: erledigt (BRIDGE-0042 PASS).
- **G1** Architektur: erledigt (BRIDGE-0043 FREIGEGEBEN); weitere Codeauftraege erst nach BRIDGE-0047.
- **G2** Stufe A: gilt erst nach PASS BRIDGE-0055 Teil A + Eintrag `G2: IN KRAFT` durch April. Danach kein Executor-Push und kein Executor-Write unter tasks/, results/, audit/ (nur in `push_mode: draft`).
- **G3** Stufe B: CAS/Claim erst nach ausdruecklicher Freigabe im Chat (vor BRIDGE-0061).
- **G4** Parallelitaet: kein Parallelbetrieb ohne Ressourcenregel + Tests (BRIDGE-0063).
- **G5** Dorfschaft: keine Dorfschaft-Aenderung. Pilot read-only; WSL-Pfad von April bestaetigt.

## 6. Aenderungen
V2: Punkte 1-7 (Nummernraum, Push-Modell, Kollisionsschutz, 6 Gates, Namensreste, Topologie, Housekeeping).
V2.1: Buendelung 21 -> 12 Auftraege (0046-0066), Slash-Command statt Langblock, kein Handover-Text (R9), R6 = Arbeit vor `run finish` committen, Wiederaufnahme eingebaut.

## 7. Resume
Usage-Limit/Toolfehler: keine neue BRIDGE-ID, Auftrag unveraendert, `/acb-auftrag` erneut aufrufen (erkennt Status), nur offene Haken.

## 8. Definition of Done
Modell-Gate erfuellt, Scope eingehalten, Tests real gezaehlt, Ergebnis valide, Haken gesetzt, gepusht, Footer.

## 9. Auftragsliste (Reihenfolge strikt)
| ID | Typ | Modell | Stufe | Gate | Titel |
|---|---|---|---|---|---|
| BRIDGE-0046 | T2 | Sonnet 5 | LOW | G1 | Housekeeping (Punkt 7) + M4-Tippfehler |
| BRIDGE-0047 | Buendel | Sonnet 5 | MEDIUM | G1 | B1 Schema-Basis: push_mode, Task-Felder, Fehlercodes |
| BRIDGE-0049 | Buendel | Sonnet 5 | MEDIUM | G1 | B2 Draft-Grundlage: Schema, Ablage, task brief |
| BRIDGE-0053 | Buendel | Sonnet 5 | MEDIUM | G1 | B3 Draft write und import |
| BRIDGE-0055 | Buendel | Sonnet 5 | LOW | G2 | B4 Stufe-A-Abnahme + Executor-Regeln |
| BRIDGE-0057 | T0 | Sonnet 5 | MEDIUM | G2 | Zweischichtige Push-Sperre: Nachweis |
| BRIDGE-0059 | T1 | Opus 5 | MEDIUM | G2 | Entscheidung Audit-Strategie |
| BRIDGE-0060 | Buendel | Sonnet 5 | MEDIUM | G2 | B5 Store-Haertung: atomar + Writer-Lock |
| BRIDGE-0061 | Buendel | Sonnet 5 | MEDIUM | G3 | B6 Stufe B: Version/CAS + Claim/Lease |
| BRIDGE-0063 | Buendel | Sonnet 5 | MEDIUM | G4 | B7 Ressourcenregel + Parallelitaetstests |
| BRIDGE-0068 | T1 | Opus 5 | MEDIUM | - | Entscheidung Windows-Benachrichtigung |
| BRIDGE-0065 | T2 | Sonnet 5 | MEDIUM | G5 | Dorfschaft: read-only Profil + Checkliste |
| BRIDGE-0066 | T3 | Codex-Modell (April tragen ein) | LOW | G5 | Dorfschaft Read-only-Pilot |
