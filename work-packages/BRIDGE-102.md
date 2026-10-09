# BRIDGE-0102: Pruefskript fuer WP-Kopf + Staging-YAML vor Uebergabe (wp-lint.py)

| Feld | Wert |
|---|---|
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - T2 additiv, aber `.claude/commands/acb-auftrag.md` ist prozesskritisch (Modell-Gate selbst), daher nicht LOW. |
| Modellwechsel zum Vorgaenger | NEIN (Vorgaenger BRIDGE-0101: Claude Sonnet 5 / MEDIUM, BUGFIX) |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `scripts/wp-lint.py`, `tests/test_wp_lint.py`, `.claude/commands/acb-auftrag.md`, `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` |

## Anlass

April (Steuerchat, 09.10.2026): BRIDGE-0101 wurde von Claude Code korrekt mit
`MODEL_GATE_UNDEFINED` BLOCKED, weil `work-packages/BRIDGE-101.md` die in
`acb-auftrag.md` §0 verlangte Modell/Denkstufe-Zeile fehlte. Befund beim
Nachpruefen: von den letzten elf Work-Packages (BRIDGE-090 bis -100) hatten
nur zwei (090/091) diese Zeile - neun liefen trotzdem durch, ohne dass es
auffiel. Die Regel existiert nur als Text in `acb-auftrag.md`, ihre
Einhaltung wird bisher ausschliesslich durch Claude Codes eigene Lektuere
des WP geprueft - nicht mechanisch, nicht vor der Uebergabe durch den
Steuerchat. April: das widerspricht dem ACB-Grundsatz fail-closed
(Durchsetzung statt Erinnerung).

## Ergebnis

`scripts/wp-lint.py` (stdlib, analog `scripts/steuerchat-vorlage.py`):

Aufruf: `.venv/Scripts/python.exe scripts/wp-lint.py --wp work-packages/BRIDGE-xxx.md --staging tasks/incoming/BRIDGE-0xxx.yaml`

Prueft, fail-closed, Exit 0 nur wenn ALLES zutrifft:

1. WP-Kopf enthaelt eine Tabellenzeile `Modell / Denkstufe` mit einem
   nichtleeren Modellnamen und einer gueltigen Denkstufe
   (`LOW`/`MEDIUM`/`HIGH`).
2. Staging-YAML validiert gegen `schemas/task.schema.yaml` (wiederverwendet
   `Store.validate`/`jsonschema`, keine Doppelimplementierung der
   Schema-Pruefung) UND enthaelt `model`/`reasoning_level` nicht-leer.
3. Modell + Denkstufe aus WP-Zeile 1 stimmen mit `model`/`reasoning_level`
   aus der YAML ueberein (exakter String-Abgleich) - genau die Luecke, die
   bei BRIDGE-0101 auftrat (YAML hatte `model`, WP-Kopf fehlte ganz).
4. `bridge_task_id` aus der YAML kommt in der WP-Ueberschrift vor (grobe
   ID-Konsistenzpruefung, analog `steuerchat-vorlage.py`).

Bei jedem Verstoss: genau benannte Fehlermeldung auf stderr (Datei+Zeile wo
moeglich), Exit-Code 1, keine Teilpruefung als "bestanden" ausgeben.

`.claude/commands/acb-auftrag.md` §0 wird um einen Verweis ergaenzt: ist
`scripts/wp-lint.py` vorhanden, ruft Claude Code es vor der eigenen
Kopf-Lektuere auf und uebernimmt dessen Exit-Code, statt den Kopf nur selbst
zu lesen - macht die Pruefung deterministisch statt modellabhaengig.

`docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 3 (Kommunikationsform) wird
um einen Punkt ergaenzt: der Steuerchat selbst ruft `wp-lint.py` lokal auf,
bevor ein WP+Staging-YAML als Datei geliefert wird (sofern das Skript im
gerade geklonten Repo bereits existiert), und nennt das Ergebnis kurz in der
Lieferzeile.

## Akzeptanzkriterien

- [x] `wp-lint.py` lehnt ein WP ohne Modell/Denkstufe-Zeile ab (Regressionstest:
  Kopie von `work-packages/BRIDGE-095.md`, das diese Zeile nachweislich nicht
  hat - Exit 1, konkrete Fehlermeldung)
- [x] `wp-lint.py` akzeptiert ein vollstaendiges Paar (Test mit
  `work-packages/BRIDGE-090.md` + einer dazu passenden, minimalen Test-YAML)
- [x] Erkennt Modell/Denkstufe-Abweichung zwischen WP und YAML (Test:
  WP sagt MEDIUM, YAML sagt LOW -> Exit 1)
- [x] Erkennt `bridge_task_id`-Inkonsistenz zwischen WP-Titel und YAML
- [x] YAML-Schema-Verstoss (z. B. fehlendes `acceptance_criteria`) wird ueber
  die bestehende Schema-Validierung erkannt, keine eigene Feldliste gepflegt
- [ ] `acb-auftrag.md` §0 referenziert das Skript, bestehendes Verhalten ohne
  das Skript (falls in einem anderen Checkout nicht vorhanden) unveraendert
- [ ] `ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 3 nennt die neue
  Steuerchat-Pflicht
- [ ] Volle Suite gruen
