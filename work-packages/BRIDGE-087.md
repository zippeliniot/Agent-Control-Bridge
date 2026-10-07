# BRIDGE-0087 - Toten Whitelist-Eintrag kind="claim" aus gitops.expected_git_files entfernen

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0087 |
| project_id | agent-control-bridge |
| Typ / Klasse | REFACTOR |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| **Modell / Denkstufe** | **Sonnet 5 / LOW** — mechanische, lokal begrenzte Entfernung eines bereits per Entscheidung (BRIDGE-0079, v15 §6 Option 2) totgelegten Codepfads, keine eigene Entwurfsentscheidung noetig. |
| depends_on | BRIDGE-0086 (ARCHIVED) |

> Anlass: offener Punkt aus v16 §6 Punkt 3 ("Toter Whitelist-Eintrag `kind="claim"` ... entfernen
> oder bewusst als zukuenftige Reserve stehenlassen, einmal final entscheiden"). April-Entscheidung
> im Steuerchat (07.10.): entfernen.
>
> Befund (Steuerchat, gegen echten Code geprueft): `claim`/`renew`/`release` committen seit
> BRIDGE-0078 ausschliesslich ueber die isolierte `_sync_claim_commit()` in `claim.py` - kein
> Aufrufer in `cli.py`/`webui.py` uebergibt `kind="claim"` an `gitops.git_commit`/
> `expected_git_files`. Der `if kind == "claim":`-Zweig in `gitops.py` (Zeilen ~102-105) ist seit
> der BRIDGE-0079-Entscheidung (Konsolidierung von `claim.py` auf `gitops.git_commit` verworfen,
> siehe `docs/handover/ACB-UEBERGABE-v15.md` §6 Punkt 1 Option 2) dauerhaft unerreichbar, nicht nur
> "noch nicht verdrahtet".
>
> **Wichtig, nicht aus der Doku allein ersichtlich gewesen:** `tests/test_gitops.py` enthaelt
> `test_claim_exact_path_only`, das genau diesen Zweig direkt (unit-level, nicht ueber einen echten
> Aufrufer) prueft. Der Zweig ist also nicht tot im Sinne von "ungetestet", sondern tot im Sinne von
> "kein Produktions-Aufrufer" - der Test muss mitgeaendert werden, sonst schlaegt die Suite nach der
> Entfernung fehl.

### Teil A - Toten Zweig entfernen

**Scope:** `src/bridge/gitops.py`.

1. In `expected_git_files()`: den Block
   ```python
   if kind == "claim":
       # BRIDGE-0078: claim/renew/release beruehren ausschliesslich die
       # eigene claim.json - exakter Pfad, kein Praefix-Match.
       return [f"results/{task_id}/claim.json"]
   ```
   vollstaendig entfernen (inkl. Kommentar).
2. Kein Ersatz-Zweig, kein Platzhalter. `kind="claim"` faellt danach auf das generische
   `base`-Verhalten zurueck (`[tasks/<id>/task.yaml, audit/audit.jsonl]`, ohne `finish`/`run_start`-
   Ergaenzung) - das ist fuer einen Wert ohne Produktions-Aufrufer folgenlos, siehe Befund oben.
3. Docstring von `expected_git_files()` (Zeilen ~91-96, "Web-UI-Arten" / "CLI-Arten") listet `claim`
   ohnehin nicht auf - keine Aenderung dort noetig, nur pruefen, dass das weiterhin stimmt.
- [x] `if kind == "claim": ...`-Block vollstaendig entfernt, keine Restspuren (Kommentar/Code)
- [x] `expected_git_files("claim", "BRIDGE-xxxx")` liefert danach `["tasks/BRIDGE-xxxx/task.yaml", "audit/audit.jsonl"]`

### Teil B - Test nachziehen

**Scope:** `tests/test_gitops.py`.

1. `test_claim_exact_path_only` (prueft aktuell `expected_git_files("claim", "BRIDGE-0006") ==
   ["results/BRIDGE-0006/claim.json"]`) entfernen - das geprüfte Verhalten existiert nach Teil A
   nicht mehr.
2. Direkt an der entfernten Stelle einen kurzen Kommentar hinterlassen (kein Test-Stub), der
   erklaert, warum hier kein Test mehr steht: Verweis auf BRIDGE-0087 und die BRIDGE-0079-
   Entscheidung (claim.py bleibt bewusst isoliert, `kind="claim"` ist kein gueltiger Whitelist-Typ
   mehr).
3. `test_project_settings_exact_path_only` (direkt danach im selben Testfile) bleibt unveraendert -
   nicht verwechseln, nicht mit entfernen.
- [x] `test_claim_exact_path_only` entfernt
- [x] Kurzer erklaerender Kommentar an der Stelle, mit Verweis auf BRIDGE-0087
- [x] `test_project_settings_exact_path_only` unveraendert vorhanden

## Abschluss
1. Volle Suite EINMAL, nur die letzten 3 Zeilen zeigen.
2. `git status` sauber.
- [ ] Volle Suite gruen (575/575 erwartet - ein Test entfernt, keiner neu)
