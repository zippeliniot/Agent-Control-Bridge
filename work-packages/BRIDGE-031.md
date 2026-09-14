# BRIDGE-031 — Maschinenauflösung vereinheitlichen: COMPUTERNAME-Autodefault an allen Schreibstellen + BRIDGE_MACHINE-Inkonsistenz beseitigen

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0031 |
| project_id | codex-control-bridge |
| task_class | BUGFIX |
| depends_on | (keine) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen) |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe MEDIUM — berührt drei Dateien (`cli.py`, `webui.py`, `importer.py`) mit mehreren Aufrufstellen, aber das Muster ist an jeder Stelle identisch und vollständig vorgegeben (bestehende Funktion `registry.machine_name()` verdrahten statt neu entwerfen), kein neues Sicherheitsmodell, keine neue Architektur. Kein Opus nötig (kein Entwurf, keine Mehrdeutigkeit), Haiku zu schwach für konsistente Änderungen an mehreren, teils zirkularitätssensiblen Modulen (Import-Reihenfolge `registry`/`store`/`profiles`). |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit` (BRIDGE-025), und **sofort**, nicht gesammelt.

## Kontext

Aus Übergabe v9, Abschnitt 0 Punkt 4: April meldete nach BRIDGE-030, dass
die Maschinen-Spalte überall nur `"?"` zeigt. Root Cause dort bereits grob
benannt, **vor dieser Spezifikation erneut frisch gegen den echten Code
geprüft** (Verifikationspflicht Nr. 3, nicht aus der Übergabe übernommen):

### Befund 1 — Audit-Schreibstellen lösen nie eine Maschine auf

`src/bridge/registry.py` hat eine fertige, korrekte Funktion
`machine_name(explicit=None)`: `explicit` → sonst `COMPUTERNAME` aus der
Umgebung → sonst `platform.node()` als Fallback. Diese Funktion wird
**ausschließlich** innerhalb von `resolve_base()` aufgerufen (Pfadauflösung
für `bridge board`/`bridge commands`) — **nirgendwo sonst**. Konkret, jede
Stelle einzeln gegen den Code geprüft:

- `cli.py` `task_copied()` (Zeile 252): ruft `store.set_status(..., None, ...)`
  — **hartkodiertes** `None`, kein Parameter dafür vorhanden. Der Parser für
  `task copied` hat außerdem gar kein `--machine`-Flag (anders als
  `set-status`/`set-priority`/`run *`).
- `cli.py` `task_archive()` (Zeile 274): dieselbe hartkodierte `None`-Stelle,
  `task archive`-Parser hat ebenfalls kein `--machine`-Flag.
- `cli.py` `_cmd_task`, Zweig `set-status` (Zeile 329f.): `machine=args.machine`
  — Flag existiert, aber `args.machine` ist `None`, solange niemand manuell
  `--machine <name>` tippt. Kein Fallback auf `machine_name()`.
- `cli.py` `task_set_priority()` (Zeile 256): gleiches Muster, `args.machine`
  roh durchgereicht.
- `cli.py` `run start`/`beat`/`finish`/`resume` (Aufrufe von `runner.start`/
  `runner.beat`/`runner.finish`/`runner.resume`): alle reichen `args.machine`
  roh durch. `runner.py` selbst (`start`/`beat`/`finish`/`resume`, je
  `machine=None`-Default) löst ebenfalls nichts auf, reicht nur weiter an
  `store.set_status`/`heartbeat.beat`.
- `webui.py`: Die Aktions-Endpunkte rufen dieselben `task_copied`/
  `task_archive`-Funktionen aus `cli.py` (kein Parallel-Code, wie
  dokumentiert) — geerbt also dieselbe hartkodierte `None`. Zusätzlich
  hartkodiert `/api/run/<id>/finish` (Zeile 255) explizit
  `machine=None` beim Aufruf von `runner.finish()`.

**Nachgezählt am echten Store:** 0 von 144 Audit-Einträgen im gesamten
Projektverlauf haben je einen `machine`-Wert gesetzt (deckt sich mit v9).

### Befund 2 — zweiter, unabhängiger Mechanismus mit demselben Symptom (neu, nicht in v9 erwähnt)

`src/bridge/importer.py`, `import_result()` (Zeile 154):
`machine = machine or os.environ.get("BRIDGE_MACHINE")` — eine **zweite,
eigene** Env-Var, komplett unabhängig von `registry.machine_name()`/
`COMPUTERNAME`. Wird für zwei Felder in `result.yaml` verwendet: den
`physical_machine`-Eintrag (Zeile 194) und den `created_by`-String
(Zeile 171: `f"{executor}@{machine or 'unknown'}"`). `BRIDGE_MACHINE` wird
nirgendwo im Repo gesetzt — weder in `CLAUDE.md` noch in einem Skript —
außer einer beiläufigen Erwähnung in `work-packages/BRIDGE-007.md`. Das
erklärt den in der echten Auditspur sichtbaren Actor
`claude-code@unknown` bei jedem `RESULT_WRITTEN`-Ereignis (z. B.
BRIDGE-0029, BRIDGE-0030). **April-Entscheidung (bestätigt):** wird
zusammen mit Befund 1 repariert, eine einzige Quelle der
Maschinenauflösung im ganzen System statt zwei inkonsistenter.

### Nicht angetastet (bewusst, wie in v9 bereits festgelegt)

- Bestehende Audit-Einträge (0/144 mit `machine`) werden **nicht**
  rückwirkend korrigiert/befüllt — reine Vorwärtskorrektur ab diesem
  Auftrag.
- `resolve_base()`/`board`/`commands` funktionieren bereits korrekt und
  bleiben unverändert — nur zusätzliche Aufrufstellen kommen hinzu.
- Kein Verhalten von `machine_name()` selbst ändern (Signatur, Fallback-
  Reihenfolge) — nur zusätzlich verdrahten. Die Funktion wirft nie
  (anders als `resolve_base`), also keine neuen Fehlerfälle durch diesen
  Auftrag.

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0031.yaml
   bridge run start BRIDGE-0031 --actor claude-code
   ```

2. **`src/bridge/cli.py`:**
   - `--machine`-Argument zu den Parsern `task copied` und `task archive`
     ergänzen (Muster wie bei `set-status`/`set-priority`: optional, kein
     `required=True`).
   - `task_copied(store, task_id, actor, machine=None)`: neuer Parameter,
     `store.set_status(task_id, "REVIEW_REQUIRED", actor,
     registry.machine_name(machine), reason=...)` statt der hartkodierten
     `None`.
   - `task_archive(store, task_id, actor, reason=None, machine=None)`:
     gleiches Muster, `registry.machine_name(machine)` statt `None`.
   - `task_set_priority(...)`: `registry.machine_name(machine)` statt
     `machine` roh an `store.set_priority` weiterreichen.
   - In `_cmd_task` (Aufrufe von `task_copied`/`task_archive`/
     `task_set_priority`) sowie im `set-status`-Zweig: `args.machine`
     jeweils via `registry.machine_name(args.machine)` auflösen, bevor es
     weitergereicht wird.
   - In `_cmd_run` (Aufrufe von `runner.start`/`runner.beat`/
     `runner.finish`/`runner.resume`): `args.machine` jeweils vor der
     Übergabe via `registry.machine_name(args.machine)` auflösen.
   - `_cmd_result_import`: `args.machine` vor der Übergabe an
     `importer.import_result(..., machine=...)` ebenfalls über
     `registry.machine_name(args.machine)` auflösen (ersetzt implizit die
     `BRIDGE_MACHINE`-Fallback-Notwendigkeit für den CLI-Pfad, siehe
     Schritt 4).
   - `registry` ist in `cli.py` bereits importiert — kein neuer Import
     nötig.

3. **`src/bridge/webui.py`:**
   - `from bridge import registry` ergänzen (kein Zirkularimport:
     `registry.py` importiert weder `webui` noch `cli`).
   - Aufrufe von `task_copied`/`task_archive` in den Aktions-Endpunkten:
     `machine=registry.machine_name()` übergeben (kein Override aus einer
     Web-Anfrage vorgesehen — immer Auto-Erkennung wie bisher bei
     `board`/`commands`).
   - `/api/run/<id>/finish` (Zeile ~255): `machine=None` durch
     `machine=registry.machine_name()` ersetzen.

4. **`src/bridge/importer.py`:**
   - `from bridge import registry` ergänzen (kein Zirkularimport:
     `registry.py` importiert `importer.py` nicht, `importer.py` hat
     aktuell gar keine `bridge`-internen Imports).
   - Zeile 154 `machine = machine or os.environ.get("BRIDGE_MACHINE")`
     ersetzen durch `machine = machine or registry.machine_name()` —
     dieselbe Quelle wie überall sonst. `BRIDGE_MACHINE` danach an
     keiner Stelle im Code mehr referenziert (grep-bar verifizieren,
     `work-packages/BRIDGE-007.md` ist ein historisches Dokument und
     bleibt unverändert, keine rückwirkende Doku-Korrektur alter
     Work-Packages).

5. **Tests** (neue Fälle, bestehende Muster wiederverwenden, kein Mocken
   von `registry.machine_name()` nötig — stattdessen `--machine <wert>`
   explizit übergeben bzw. `COMPUTERNAME` in der Testumgebung setzen,
   analog `tests/test_registry.py`):
   - `tests/test_cli.py`: `task copied`, `task archive`, `task set-status`,
     `task set-priority`, `run start`, `run beat`, `run finish`,
     `run resume` — je ein Test, der ohne `--machine`-Flag aufruft, dabei
     `COMPUTERNAME` in der Testumgebung setzt, und prüft, dass der
     resultierende Audit-Eintrag (`audit/audit.jsonl`, letzter Eintrag der
     jeweiligen `bridge_task_id`) das gesetzte `machine`-Feld trägt (nicht
     `null`). Zusätzlich je ein Test mit explizitem `--machine XYZ`, der
     `XYZ` unverändert im Audit-Eintrag zeigt (Override-Vorrang bleibt
     erhalten).
   - `tests/test_webui.py`: mindestens ein Test pro Aktions-Endpunkt
     (`copied`, `archive`, `run finish`), der `COMPUTERNAME` setzt und
     prüft, dass der geschriebene Audit-Eintrag die Maschine trägt (bisher
     ungetesteter Pfad).
   - `tests/test_importer.py`: Test, der `import_result()` ohne expliziten
     `machine`-Parameter aufruft, `COMPUTERNAME` gesetzt, `BRIDGE_MACHINE`
     **nicht** gesetzt — `result.yaml` (`physical_machine`) und
     `created_by` müssen die über `COMPUTERNAME` aufgelöste Maschine
     zeigen, nicht `"unknown"`. Zusätzlich ein Test mit explizitem
     `machine="X"` — Vorrang vor `COMPUTERNAME` bleibt erhalten
     (bestehendes Verhalten von `machine_name()`, nur jetzt tatsächlich
     erreicht).
   - Bestehende Tests, die bewusst einen leeren/`"?"`-Zustand prüfen
     (`test_overview_missing_machine_shown_as_question_mark`,
     `test_board_rows_includes_machine_question_mark_fallback`), bleiben
     unverändert grün — die dort simulierten Fälle (kein Heartbeat, kein
     Audit-Eintrag vorhanden) sind unabhängig von diesem Fix weiterhin
     möglich (z. B. bei einem sehr alten/manuell erzeugten Auftrag ohne
     jede Aktion) und correct sein.
   - Volle Testsuite frisch laufen lassen, dreimal, tatsächlich
     nachzählen (aktueller Referenzwert: 322 Tests vor diesem Auftrag,
     plus die neuen Fälle aus diesem Schritt).

6. **Dokumentation:**
   - `docs/CCB-STEUERCHAT-REFERENZ.md`, Abschnitt 0 des Handover-Hinweises
     zum Maschinenwechsel bzw. Teil 4 (Web-UI-Referenz, Maschinen-Spalte):
     kurzen Hinweis ergänzen, dass die Maschinenauflösung ab BRIDGE-0031
     an allen Schreibstellen aktiv ist (COMPUTERNAME-Autodefault greift
     jetzt auch ohne manuelles `--machine`).
   - Kein Abschnitt in `SECURITY-MODEL.md` nötig — reine
     Funktionsverdrahtung, keine neue Rechte-/Sicherheitsentscheidung.

7. Pflicht-Footer + Abschluss, `--commit` nutzen, **sofort pushen**:
   ```
   bridge run finish BRIDGE-0031 --status COMPLETED --actor claude-code \
     --commit \
     --summary "registry.machine_name() (COMPUTERNAME-Autodefault) jetzt an allen Audit-Schreibstellen verdrahtet: task_copied()/task_archive() (bisher hartkodiertes None, jetzt --machine-Flag + Aufloesung), task set-status/set-priority, run start/beat/finish/resume (bisher rohes args.machine ohne Fallback), webui.py-Aktionsendpunkte (bisher teils hartkodiertes None). Zusaetzlich zweiten, unabhaengigen Mechanismus in importer.py vereinheitlicht: BRIDGE_MACHINE-Env-Var (nie gesetzt, verursachte 'actor@unknown' in result.yaml/created_by) durch registry.machine_name() ersetzt - eine einzige Quelle der Maschinenaufloesung im gesamten System. Bestehende Audit-Eintraege bewusst nicht rueckwirkend korrigiert (Vorwaertskorrektur)."
   git push
   ```
   `Auftrag: BRIDGE-0031 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [x] `task copied` und `task archive` haben ein optionales `--machine`-Flag
      (Parität zu `set-status`/`set-priority`/`run *`).
- [x] `task_copied()`/`task_archive()`/`task_set_priority()` lösen die
      Maschine über `registry.machine_name(machine)` auf statt `None`
      hartzukodieren oder roh durchzureichen.
- [x] `run start`/`beat`/`finish`/`resume` (CLI) lösen `args.machine` vor
      Übergabe an `runner.*` über `registry.machine_name()` auf.
- [x] `result import` (CLI) löst `args.machine` ebenso auf.
- [x] `webui.py`-Aktionsendpunkte (`copied`, `archive`, `run finish`)
      übergeben `registry.machine_name()` statt `None`.
- [x] `importer.import_result()` nutzt `registry.machine_name()` statt der
      `BRIDGE_MACHINE`-Env-Var; `BRIDGE_MACHINE` wird im Code nirgendwo
      mehr referenziert.
- [x] Ohne `--machine`/expliziten `machine`-Parameter und mit gesetztem
      `COMPUTERNAME`: neue Audit-Einträge sowie `result.yaml`
      (`physical_machine`, `created_by`) tragen die aufgelöste Maschine,
      nicht `null`/`"unknown"`.
- [x] Mit explizitem `--machine`/`machine=`-Parameter: dieser hat weiterhin
      Vorrang vor `COMPUTERNAME` (bestehendes Verhalten von
      `machine_name()` unverändert).
- [x] Bestehende Tests für den `"?"`-Fallback-Fall (kein Heartbeat, kein
      Audit-Eintrag) bleiben unverändert grün.
- [x] Neue Tests in `test_cli.py`, `test_webui.py`, `test_importer.py` für
      alle oben gelisteten Aufrufstellen, grün.
- [x] Bestehende Audit-Einträge unverändert (keine rückwirkende
      Korrektur).
- [x] `CCB-STEUERCHAT-REFERENZ.md` um den Hinweis zur jetzt aktiven
      Autoauflösung ergänzt.
- [x] Volle Testsuite (bestehend + neu) dreimal frisch grün, frischer
      Klon verifiziert.
- [x] Jeder Commit sofort gepusht, nicht gesammelt.

## RUN-01 — Hinweis zur Commit-Historie

Die Implementierung in `src/bridge/cli.py`/`webui.py`/`importer.py` (Abschnitt
2-4) wurde lokal umgesetzt und zum Commit vorgemerkt (`git add`), landete dann
aber nicht unter einer eigenen BRIDGE-0031-Commit-Message, sondern wurde von
einem **parallelen Prozess im selben Arbeitsverzeichnis** (Commit `f6b26c2`,
Nachricht "Docs: Standardstart-Prompt um fehlende Verifikationspflichten aus
ARBEITSWEISE.md ergaenzt") mit committet und bereits gepusht, bevor dieser
Lauf selbst committen konnte. Der Dateiinhalt wurde per `git diff` gegen die
Spezifikation verifiziert — identisch zu dem, was dieser Auftrag umsetzen
sollte, keine fremden/unerwuenschten Aenderungen an diesen drei Dateien.
Die anschliessenden Schritte (Tests, Doku, dieses Register) wurden regulaer
unter eigenen BRIDGE-0031-Commits committet und sofort gepusht.
