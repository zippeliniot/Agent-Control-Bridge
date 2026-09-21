# ACB - Uebergabe v12 (Rotation DES11 -> HAM11)

**Stand:** 2026-09-20 | **Repo-HEAD bei Erstellung:** e8dfa51 (danach nur Ops-Commits der Web-UI und diese Datei) | **Tests:** 452/452 gruen
**Fuer den neuen Steuerchat:** docs/ACB-STEUERCHAT-STANDARDSTART.md, docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md (V2.1) und diese Datei.

## 1. Stand der Umsetzung (Konzept V2.1, Auftraege 0042-0066)
Erledigt und archiviert: 0042 Baseline, 0043 Push-Modell (Option B, FREIGEGEBEN), 0044 Namensreste, 0045 Topologie, 0046 Housekeeping,
0047 Schema-Basis (push_mode, Task-Felder, error-codes), 0049 Draft-Grundlage, 0053 draft write/import + task brief,
0067 Nachbesserung draft (Einschub), 0055 Stufe-A-Abnahme + Executor-Regeln, 0057 Push-Sperre (nachgewiesen),
0059 Audit-Strategie (Option A, FREIGEGEBEN).
0060 Store-Haertung (atomare Writes + Writer-Lock), geprueft PASS und archiviert.
**G2: IN KRAFT** (2026-09-20). Kein Projekt steht auf `push_mode: draft`, alle laufen weiter mit `direct`.

## 2. Naechste Auftraege (strikt in Reihenfolge)
| ID | Inhalt | Modell / Stufe | Voraussetzung |
|---|---|---|---|
| 0061 | B6 Stufe B: task_version/CAS + Claim/Lease | Sonnet 5 / MEDIUM | **G3-Freigabe von April** (ausdruecklich im Chat) |
| 0063 | B7 Ressourcenregel + Parallelitaetstests | Sonnet 5 / MEDIUM | nach 0061 |
| 0065 | Dorfschaft: Profil + Checkliste (kein Repo-Zugriff) | Sonnet 5 / MEDIUM | WSL-Pfad von April |
| 0066 | Dorfschaft Read-only-Pilot durch Codex | Codex / LOW | 0065 + bestaetigter WSL-Pfad + erwarteter HEAD (G5) |

Die Staging-YAMLs (`tasks/incoming/` ist gitignored) liegen versioniert unter `docs/handover/staging-v12/`.
Auf der Zielmaschine: `Copy-Item docs\handover\staging-v12\*.yaml tasks\incoming\`.

## 3. Arbeitsweise (bewaehrt)
- Start: `/clear`, `/model` (Modell + Stufe laut Tabelle, auf die richtige Zeile achten), `/acb-auftrag BRIDGE-00xx`.
  Der Ablauf steht nur in `.claude/commands/acb-auftrag.md`.
- Modell-Gate: Claude Code schreibt zuerst `MODELL: .. / DENKSTUFE: ..`, sonst STOPP (hat zweimal korrekt gegriffen).
- April schickt nur den Footer (Auftrag/Lauf/Status). Der Steuerchat prueft im FRISCHEN Klon: Task-Status, model/reasoning,
  result.yaml (head, commits und changed_files == echter Diff), Haken, HEAD == origin/main, Suite selbst laufen lassen,
  Verhalten per Experiment. Er schreibt nie ins Repo.
- Buendel = Teile A/B/C mit je eigenem Commit, Push und Haken. `run finish` erst NACH dem Arbeits-Commit.
- Web-UI (nur board-Klon): oberer Bereich = wartet auf Kopie; "Offene Auftraege ausserhalb des Boards" = REVIEW_REQUIRED u. a. (dort `Archivieren`).
- Doku-Aenderungen macht April per PowerShell-Block. Text nur per .NET ReadAllText/WriteAllText (UTF-8 ohne BOM).
- Downloads: Version im Dateinamen (Windows haengt sonst `(1)` an). ZIP-Download ging nicht: Sammeldatei mit `=== FILE: pfad ===` + Splitter.

## 4. Fallstricke (aus dieser Phase)
- Ein Auftrag kann lokal angelegt, aber nicht gepusht sein: "kein Task auf GitHub" heisst nicht "nicht angelegt".
- Paketumfang und Akzeptanzkriterien muessen zusammenpassen (0055: CONTROL.md stand nicht im Scope).
- Ist-Stand-Zahlen in Paketen vorher messen (Profile: 7 statt 8, Audit: 373 statt 260 Zeilen).
- Hoher Dauer-CPU-Verbrauch eines Python-Prozesses ohne Kommandozeile = haengendes Skript aus Claude Code; nur die zwei `webui serve`-Prozesse sind normal.
- Verifikation immer gegen echten Diff, nicht gegen die Selbstauskunft.

## 5. Offene Punkte (nicht blockierend)
- G3-Freigabe fuer 0061; WSL-Pfad + erwarteter HEAD Dorfschaft fuer 0065/0066.
- HAM11-Umstellung auf vier Klone (machines.md: HAM11 alte Topologie). Danach machines.md und docs/SETUP.md (beschreibt noch einen Klon) anpassen.
- Draft-Modus fuer ACB aktivieren ist eine eigene Entscheidung (`push_mode: draft`); Transfer per lokalem `git pull <Pfad> main` (docs/security/PUSH-SPERRE-NACHWEIS.md).
- Codex-Regel `git push` verboten waere global (~/.codex/rules): fuer `codex` nur Schicht 2 (Push-URL DISABLED) gesetzt.
- Web-UI: harmloser WinError 10053 (Browser bricht ab), spaeter still ignorieren.
- `errorcodes.is_known()` ohne schema_dir nutzt einen Modul-Cache (harmlos).
- Der Writer-Lock gilt je Klon, nicht klonuebergreifend. Klonuebergreifend schuetzen Git und die Ressourcenregel (0063).
- WP-Dateien 0039-0041 sind 4-stellig benannt (die --commit-Whitelist erwartet 3-stellig).
- Offene Haken ohne Nachweis: WP 027/028/029 (frischer Klon, Sofort-Push, Web-UI, Sortierung, Prioritaet), Rest von 0039/0040. CCB-UEBERGABE v4/v5 fehlen im Repo.

## 6. HAM11-Umstellung (erledigt 2026-09-20)
`E:\_DEV\Agent-Control-Bridge\{board,dev,claude,codex}` auf HAM11 und DES11. board = einzige Web-UI/Writer, dev = ACB-Entwicklung (Claude Code),
claude = nur Produktarbeit, codex = Codex. In `claude` und `codex`: Push gesperrt (Push-URL DISABLED; in `claude` zusaetzlich `.claude/settings.local.json`).
HAM11-Besonderheiten: Python 3.10.6 (Suite 452/452 OK, Laufzeit ca. 325 s statt ca. 60 s auf DES11). Vor jeder Rotation die Web-UI der abgebenden Maschine beenden (ein Writer).
Noch offen: `claude`-Klon auf HAM11 hatte schon eine `settings.local.json` (Inhalt/Deny-Eintraege pruefen), docs/SETUP.md beschreibt noch einen Klon.
