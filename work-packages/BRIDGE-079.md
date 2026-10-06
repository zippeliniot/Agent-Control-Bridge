# BRIDGE-0079 - Claim-Commit-Pfad auf gitops.git_commit konsolidieren (autostash)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0079 |
| project_id | agent-control-bridge |
| Typ / Klasse | REFACTOR |
| Teile (alte Nummern) | keine (neuer Auftrag) |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - enger, klar umrissener Scope (zwei Dateien), aber sicherheitsrelevanter Commit-Pfad, keine Architektur-Unsicherheit. |
| MODELL: Claude Sonnet 5 / DENKSTUFE: MEDIUM | (identisch mit tasks/incoming/BRIDGE-0079.yaml: model, reasoning_level) |
| Modellwechsel zum Vorgaenger | NEIN (BRIDGE-0078 war ebenfalls Claude Sonnet 5 / MEDIUM, vergleichbarer Scope-Zuschnitt) |
| depends_on | BRIDGE-0078 (ARCHIVED) |
| Gate | keines |
| stop_conditions | CONCEPT_CONFLICT, SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0079` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

**Vorbedingung (vor Teil A pruefen, nicht annehmen):** `src/bridge/gitops.py` Funktion `expected_git_files` enthaelt bereits den `kind == "claim"`-Zweig (`results/<task_id>/claim.json`, BRIDGE-0078 Teil A) - dieser Auftrag erweitert `git_commit`, er legt den Whitelist-Eintrag nicht neu an. Steht der Zweig nicht mehr dort: STOPP, `CONCEPT_CONFLICT`.

## Auftrag

**Ziel:** `claim`/`renew`/`release` committen/pushen kuenftig ueber den einen gemeinsamen, whitelist-geguardeten Pfad `gitops.git_commit()` statt ueber einen eigenstaendigen zweiten Commit/Push-Mechanismus in `claim.py`. Der bisherige Grund fuer die Abspaltung (`gitops.git_commit`'s Rebase-Retry verlangt einen sauberen Baum, waere also bei einem parallel anstehenden, nicht committeten Audit-Eintrag gescheitert) wird durch einen neuen `autostash`-Parameter aufgeloest statt durch eine Parallel-Implementierung.

### Teil A - `autostash`-Parameter in `gitops.git_commit`

**Scope:** `src/bridge/gitops.py` (Funktion `git_commit`, ab Zeile 138), `tests/test_gitops.py`.

1. `git_commit(..., autostash: bool = False)` - neuer Keyword-Parameter, Default erhaelt bestehendes Verhalten fuer alle existierenden Aufrufer (`cli.py`, `webui.py`) unveraendert.
2. Im Rebase-Retry-Schritt (NFF-Pfad, "6b." im bestehenden Code): bei `autostash=True` `git rebase --autostash origin/<branch>` statt `git rebase origin/<branch>`. Rebase-Abbruch-Verhalten (`rebase --abort` bei Konflikt) bleibt unveraendert.
3. Keine Aenderung an Branch-Pruefung, Whitelist-Pruefung, Force-Push-Verbot (BRIDGE-024-Sicherheitsleitplanken) - nur der eine Rebase-Aufruf wird parametrisiert.

**Tests:** gezielter Testfall mit echtem bare-Repo: lokale `git_commit(..., autostash=True)`-Operation waehrend eine zweite, unabhaengige Datei im Arbeitsbaum unstaged/uncommitted vorliegt und gleichzeitig ein Non-Fast-Forward-Fall vorliegt - Rebase darf trotz der fremden Datei nicht an "dirty tree" scheitern. Danach `python -m unittest tests.test_gitops`, dann volle Suite EINMAL.
- [ ] `autostash`-Parameter implementiert, Default-Verhalten fuer bestehende Aufrufer unveraendert (Regressionstest)
- [ ] Autostash-Testfall (dirty tree + NFF) gruen

### Teil B - `claim.py` auf `gitops.git_commit` umstellen, Duplikat entfernen

**Scope:** `src/bridge/claim.py` (`claim`/`renew`/`release` ab Zeile 412/451, `_sync_claim_commit` Zeile 345, `_push_with_retry` Zeile 311), `tests/test_claim.py`.

1. `claim()`, `renew()`, `release()` rufen nach erfolgreicher lokaler Operation `gitops.git_commit(store.root, "claim", task_id, actor, push=True, autostash=True, source=...)` auf statt `_sync_claim_commit`.
2. Push-Race-Rollback-Semantik aus BRIDGE-0078 (lokale `claim.json` entfernen/zuruecksetzen bei Pushfehler, `ClaimError("RESOURCE_CONFLICT")`) bleibt inhaltlich erhalten - jetzt ausgeloest anhand des `error`-Felds im `git_commit()`-Rueckgabedict statt anhand eigener Fehlerbehandlung.
3. `_sync_claim_commit` (Zeile 345) und `_push_with_retry` (Zeile 311) vollstaendig entfernen, sofern nach Schritt 1/2 nicht mehr referenziert.
4. Die origin/main-Vorrangslogik aus BRIDGE-0078 (`_check_resource`, Zeile 244; `_synced_claim`, Zeile 111) bleibt **unveraendert** - nicht Teil dieses Auftrags, nur der Commit/Push-Mechanismus wird konsolidiert.

**Tests:** bestehende Push-Race-Simulationstests aus BRIDGE-0078 (`claim`/`renew`/`release` je einzeln) muessen mit dem neuen Pfad weiterhin gruen sein - Testfaelle selbst nicht inhaltlich aendern, nur ggf. an die neue Aufrufkette anpassen. Dann `python -m unittest tests.test_claim tests.test_gitops`, dann volle Suite EINMAL.
- [ ] `claim`/`renew`/`release` rufen `gitops.git_commit(..., kind="claim", autostash=True)` auf
- [ ] `_sync_claim_commit`, `_push_with_retry` entfernt, keine toten Referenzen
- [ ] Push-Race-Tests aus BRIDGE-0078 weiterhin gruen (Rollback + `RESOURCE_CONFLICT`, kein haengender Zustand)

## Abschluss

1. Volle Suite EINMAL, nur die letzten 3 Zeilen zeigen. Testanzahl gegenueber BRIDGE-0078-Stand (536) nicht gesunken.
2. `git diff --stat` gegen `expected_head` zeigt ausschliesslich `src/bridge/gitops.py`, `src/bridge/claim.py`, `tests/test_gitops.py`, `tests/test_claim.py`.
3. `git status` sauber, dann Abschluss wie im Slash-Befehl.
- [ ] Volle Suite gruen
