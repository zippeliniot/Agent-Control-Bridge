# BRIDGE-0041 — Bugfix: executor/created_by in result.yaml

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0041 |
| project_id | agent-control-bridge |
| task_class | BUGFIX |
| depends_on | keine technische Abhängigkeit, aber **erst starten, wenn BRIDGE-0039/0040 archiviert sind** (Ein-Auftrag-zur-Zeit) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| executor | claude-code |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe LOW — Ursache bereits lokalisiert (`importer.py::build_result()`, `runner.py::finish()`), Fix vollständig spezifiziert, keine eigene Entwurfsentscheidung nötig. |

## Befund (Ursache bereits verifiziert, nicht neu suchen)

In `BRIDGE-0040/RUN-01/result.yaml` steht `executor: claude-code`, obwohl
der Lauf real von Codex ausgeführt wurde. Ursache:

- `src/bridge/importer.py::build_result()` hat `executor="claude-code"`
  als **hartkodierten Default-Parameter**.
- `src/bridge/runner.py::finish()` lädt das Task-Dokument bereits
  (`current = store.load_task(task_id).get("status")`), liest daraus
  aber **nicht** das vorhandene Schema-Feld `executor` und reicht es
  nicht an `importer.import_result()` durch.
- `created_by` wird zusätzlich aus diesem falschen `executor`-Wert
  abgeleitet (`created_by or f"{executor}@{machine}"`) statt aus dem
  bereits korrekt vorhandenen `actor`-Parameter — der `actor` selbst ist
  im Audit-Trail bereits richtig (z. B. `"codex-executor"` bei
  BRIDGE-0040), betroffen ist ausschließlich `result.yaml`.

## Auftrag

1. `runner.py::finish()`: `executor`-Feld aus dem bereits geladenen
   Task-Dokument lesen, an `importer.import_result()`/`build_result()`
   durchreichen.
2. `importer.py::build_result()`: `executor`-Parameter primär aus dem
   Task-Dokument übernehmen, Fallback `"claude-code"` nur, wenn das Feld
   dort fehlt (Rückwärtskompatibilität für alte Tasks ohne `executor`-
   Feld im Schema).
3. `created_by` aus dem tatsächlichen `actor`-Parameter (nicht aus
   `executor`) + `machine` bilden.
4. Zwei neue Tests: (a) Lauf mit `executor: codex` im Task → `result.yaml`
   zeigt `executor: codex`, `created_by` beginnt mit dem echten `actor`;
   (b) Lauf mit `executor: claude-code` (Normalfall) bleibt unverändert
   korrekt.
5. Keine Änderung an anderen `result.yaml`-Feldern.

## Pflichtblock — Auftrags-Lebenszyklus

- Jede Zustandsänderung über die Bridge-CLI, kein direktes Bearbeiten
  von Store-Dateien.
- `GIT_PUSH` ist im Berechtigungsprofil gesetzt — nach `run finish` sofort
  pushen (normale Regel, **keine** Ausnahme wie bei BRIDGE-0039/0040).
- `run finish --commit --summary "..." --from draft.yaml` verwenden,
  damit `acceptance_results` vollständig im Ergebnis landen.

## Akzeptanzkriterien

- [ ] `executor` in `result.yaml` stammt aus dem Task-Dokument, nicht aus
      einem hartkodierten Default
- [ ] `created_by` stammt aus dem tatsächlichen `actor` + `machine`
- [ ] Neuer Test: Codex-Lauf liefert korrekten `executor`/`created_by`
- [ ] Neuer Test: Claude-Code-Lauf weiterhin korrekt (Regressionsschutz)
- [ ] Testsuite komplett grün, frisch in isoliertem venv, tatsächlich
      nachgezählt (aktuell 381 Tests als Ausgangsbasis)
- [ ] Keine Änderung an anderen `result.yaml`-Feldern
