# ACB - Uebergabe v13 (Stand 2026-09-23)

**Repo-HEAD bei Erstellung:** 899f9f8 | **Tests:** 505/505 gruen (500 + 5 aus BRIDGE-0071)
**Fuer den neuen Steuerchat:** docs/ACB-STEUERCHAT-STANDARDSTART.md, docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md (V2.1) und diese Datei. v12 nicht loeschen (Historie).

## 1. Was sich seit v12 geaendert hat
Erledigt und archiviert: 0061 (task_version/CAS + Claim/Lease, G3 freigegeben 2026-09-21), 0063 (Ressourcenregel +
Parallelitaetstests, **G4 IN KRAFT**), 0065 (Dorfschaft: read-only Checkliste, Windows-Pfad statt WSL dokumentiert),
0068 (T1-Entscheidung Windows-Benachrichtigung, Option A FREIGEGEBEN), 0069 (webui serve --notify umgesetzt),
0070 (Toast-Fix: eigene Kennung wird von Windows verworfen, jetzt PowerShell-AUMID), 0071 (Steuerchat-Vorlage
automatisch aus project.yaml fuellen, executor-bewusst claude-code/codex).

**Neu: erstes Fremdprojekt produktiv.** wetter-app (zippeliniot/wetter-app, live wetter.gronenberg.info) ist das
erste Projekt ueber das Profil-System (projects/wetter-app/project.yaml). WETTER-0001 (precipitation_probability +
dichtere Abtastung; DWD-Radar-Teil nicht umsetzbar, RADOLAN binaer ohne CORS) und WETTER-0002 sind archiviert.

**Neu: Klon-Konvention.** `E:\_DEV\Agent-Control-Bridge\projects\<projekt-id>` ersetzt `claude\` fuer neue
Auftraege bei Fremdprojekten (2026-09-22, machines.md aktualisiert) - ein Klon pro Projekt, beliebig viele
parallel. Der Zielcode selbst liegt weiter in seinem eigenen, unabhaengigen lokalen Pfad (z. B. E:\_DEV\Wetter-App).

**Neu: mehrere Steuerchats.** Fuer wetter-app laeuft jetzt ein eigener, separater claude.ai-Chat/-Projekt
(docs/handover/WETTER-STEUERCHAT-UEBERGABE.md als dessen Uebergabe). Dieser Chat hier (ACB-Kernentwicklung)
prueft WETTER-Auftraege NICHT mehr mit. Fuer weitere Fremdprojekte: docs/ACB-STEUERCHAT-VORLAGE.md +
scripts/steuerchat-vorlage.py --project-id <id> liefert den fertigen, tippfehlerfreien Prompt fuer ein neues
claude.ai-Projekt (Custom Instructions).

## 2. G-Status
- G0-G4: erledigt/in Kraft.
- **G5 (Dorfschaft) NICHT erreicht.** 0066 (Read-only-Pilot durch Codex) ist NICHT gestartet. Blocker: der
  Dorfschaft-Worktree AP15-RP2-HAM01 ist seit dem WSL-Wegfall auf HAM11 fuer Windows-Git nicht mehr oeffenbar
  (`git worktree list --porcelain` zeigt ALLE Worktrees als "prunable, gitdir file points to non-existent
  location"). Nur das Hauptrepo E:\_DEV\dorfschaft (main, HEAD 138f9717c0de4224859494a07a1366fc1faa0cfa) ist
  unter Windows-Git nutzbar. **Offene Entscheidung von April** (nicht raten): `git worktree repair` + AP15-RP2
  als Grundlage, ODER Pilot direkt auf main. Erst danach 0066 zuschneidbar.
- G6 (Codex darf produktiv/schreibend arbeiten) existiert noch nicht als Konzept, waere nach erfolgreichem 0066
  ein eigener Entscheidungsauftrag (T1).

## 3. Strukturelle Befunde (wichtig fuer naechste Fremdprojekt-Auftraege)
- `.claude/commands/acb-auftrag.md` ist NUR fuer BRIDGE-IDs geschrieben (Beispiel BRIDGE-0047 fest im Skill).
  Bei Nicht-BRIDGE-Auftraegen (WETTER-xxxx etc.) NIE den Slash-Befehl oder die Woerter "Auftrag"/"acb-auftrag"
  in der ersten Anweisung an Claude Code verwenden - der Skill greift sonst automatisch und faengt sich am
  falschen, alten Task. Stattdessen woertlich auf die WP-Datei verweisen (siehe scripts/steuerchat-vorlage.py /
  docs/ACB-STEUERCHAT-VORLAGE.md, dort schon eingearbeitet).
- `result.yaml` kennt nur EIN Repository (repository/head). Bei Auftraegen, die ein Fremdrepo aendern, steht der
  Ziel-Commit-SHA nur im freien `summary`-Text - beim Pruefen IMMER zusaetzlich das Zielrepo separat frisch
  klonen und den SHA dort verifizieren, nicht nur das ACB-Repo.
- Wiederkehrendes, harmloses Muster: der Haken "Suite gruen" bleibt trotz gruener Suite manchmal ungesetzt
  (0070, 0071) - kein Bug, nur beim Pruefen mitziehen.

## 4. Arbeitsweise (unveraendert bewaehrt, siehe v12 §3)
Frischer Klon vor jeder Pruefung, echter Diff statt Selbstauskunft, Haken/HEAD/Suite/Verhalten pruefen, nie
selbst ins Repo schreiben, Governance-Aktionen (copied/archive/run finish) nie selbst ausfuehren.

## 5. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
- G3 ist freigegeben (gilt fuer 0061/Claim-Lease) - nicht erneut nachfragen.
- Klon-Konvention `projects\<projekt-id>` ist beschlossen, ersetzt `claude\` - nicht zur alten Konvention
  zurueckfallen.
- WETTER-Auftraege gehoeren in den separaten Wetter-Steuerchat, nicht hierher.
- Die Worktree-Entscheidung fuer Dorfschaft/0066 liegt bei April - nicht raten, nicht automatisch reparieren.

## 6. Offene Punkte aus v12, weiterhin unveraendert
HAM11-Umstellung auf vier Klone: erledigt (v12 §6). Draft-Modus fuer ACB: weiterhin eigene, nicht getroffene
Entscheidung. Codex-Regel global vs. Schicht 2: unveraendert nur Schicht 2. WinError 10053: weiterhin harmlos.
Writer-Lock gilt je Klon: unveraendert, siehe 0063-Ressourcenregel. WP 027-029/039-041: weiterhin ohne
nachtraeglichen Nachweis, nicht mehr relevant.