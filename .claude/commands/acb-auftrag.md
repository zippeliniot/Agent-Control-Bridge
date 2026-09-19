---
description: ACB-Auftrag ausfuehren (Modell-Gate, Teile, Abschluss)
---
Fuehre Auftrag $ARGUMENTS aus (ID-Format BRIDGE-0047). Lies NUR:
work-packages/BRIDGE-<letzte 3 Ziffern>.md (0047 -> BRIDGE-047.md) und docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md §3.
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas
Actor = claude-code (Codex-Auftraege: codex-executor).

0 MODELL-GATE: Schreibe als erste Zeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". SOLL steht im WP-Kopf. Abweichung: STOPP, sonst nichts tun.
1 git pull. In tasks\incoming\<ID>.yaml: steht EXPECTED_HEAD -> durch `git rev-parse HEAD` ersetzen; steht schon ein SHA -> NICHT aendern.
2 Auftrag vorhanden? (BR task show <ID>)
  - nein: BR task create tasks\incoming\<ID>.yaml --commit ; git push
  - Status WAITING_FOR_HANDOFF_TO_EXECUTOR: BR run start <ID> --actor <Actor> --commit ; git push
  - Status RUNNING: weiter. Alles andere: STOPP.
3 Setze das WP um. Teile A, B, ... strikt nacheinander. Nach JEDEM Teil: Haken im WP setzen, `git add` NUR die im WP genannten Pfade + die WP-Datei, `git commit -m "<ID> Teil X: <kurz>"`, `git push`.
  Nur Einzel-Edits, keine Volltext-Ausgaben, kein git add -A, nie --force. Tests gezielt je Teil, volle Suite EINMAL am Ende, nur die letzten 3 Zeilen zeigen.
4 `git status` muss sauber sein, sonst STOPP.
5 BR run finish <ID> --status COMPLETED --actor <Actor> --commit --summary "<max 3 Saetze>" ; git push
6 Ausgabe NUR: Footer (Auftrag / Lauf / Status) + max. 3 Zeilen (Head, Tests x/y, Befunde). Kein Handover-Text.
Unklar oder Stopp-Bedingung (WP-Kopf): Status BLOCKED, Fehlercode, EIN Beweis, aufhoeren.
