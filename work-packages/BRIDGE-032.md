# BRIDGE-032 — Review-Unternummern-Schema: `-R<n>`-Suffix + fail-closed Durchsetzung von READONLY_CHECK

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0032 |
| project_id | codex-control-bridge |
| task_class | FEATURE |
| depends_on | (keine) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen) |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe MEDIUM — Schema-Pattern-Änderung an sechs synchron zu haltenden Stellen (mechanisch, aber leicht zu vergessen), plus eine neue, bisher nicht vorhandene Geschäftsregel (Kopplung `task_class`/`permissions`/ID-Suffix) mit einer echten, aber klar umrissenen Platzierungsentscheidung im Store. Kein neuer Zustand, kein neues Sicherheitsmodell — daher nicht HIGH. |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit`, und **sofort**, nicht gesammelt.

## Kontext

Ursprünglich als `BRIDGE-0030` in `docs/CCB-ORCHESTRATOR-KONZEPT.md` geplant,
durch zwei zwischenzeitlich eingeschobene Aufträge (Web-UI-Paket, dann der
COMPUTERNAME-Bugfix) zweimal verschoben — jetzt `BRIDGE-0032`. Zitat aus dem
Konzeptdokument, frisch gelesen, nicht aus einer alten Übergabe übernommen:

> „Support-KI-Prüfaufträge bekommen eine sichtbare Unternummer
> (`BRIDGE-0027-R1` usw., Schema-Pattern-Erweiterung), `task_class:
> READONLY_CHECK`, technisch auf reine Leserechte beschränkt."

**Vor der Spezifikation den echten Code geprüft (Verifikationspflicht Nr. 3),
nicht nur die Konzept-Doku übernommen** — dabei zwei Dinge festgestellt, die
das Konzeptdokument nicht erwähnt:

1. **`task_class: READONLY_CHECK` existiert bereits** im Enum von
   `schemas/task.schema.yaml` (vermutlich aus BRIDGE-012,
   `scripts/integration_readonly.py` nutzt es schon für einen
   Beobachtungs-Auftrag mit `permissions: [READ_ONLY]`). Es gibt aber
   **keine einzige Stelle im Code**, die technisch durchsetzt, dass ein
   `READONLY_CHECK`-Auftrag tatsächlich nur `READ_ONLY`-Rechte hat — weder
   in `Store.validate()` noch in `create_task()`/`save_task()`. Ein
   `READONLY_CHECK`-Auftrag mit `permissions: [GIT_PUSH]` würde heute
   anstandslos angelegt.
2. **`review_roles` ist rein anzeigend**, keine technische Durchsetzung
   irgendeiner Art (`grep -rn review_roles src/bridge/*.py`: nur
   `_board_review_roles()`/`profiles.resolve_review_roles()` für die
   Board-Spalte „Führung/Prüfung"). Es gibt **keinen Identitäts-/Auth-
   Mechanismus** im gesamten Code, der prüfen könnte, ob der tatsächliche
   Ausführende wirklich die `support`-Partei ist — `actor`/`created_by`
   sind freie Textfelder ohne Verifikation. „Technische Durchsetzung als
   Leserrolle" kann daher **nur** heißen: die **Rechte** des Auftrags
   selbst fail-closed auf `READ_ONLY` zu erzwingen (Punkt 1) — nicht eine
   Identitätsprüfung, die es in der Architektur schlicht nicht gibt und
   die dieser Auftrag nicht nachrüstet (wäre eigenes, deutlich größeres
   Thema).

**Sechs synchron zu haltende Fundstellen des aktuellen ID-Patterns**
(`^[A-Z]{1,8}-[0-9]{4}$`), einzeln per `grep` gefunden, nicht aus dem
Gedächtnis:
- `schemas/task.schema.yaml`: `bridge_task_id` (Zeile 54) **und**
  `depends_on`-Items (Zeile 212) — zwei Stellen in derselben Datei.
- `schemas/audit-event.schema.yaml` (Zeile 63).
- `schemas/result.schema.yaml` (Zeile 66).
- `schemas/heartbeat.schema.yaml` (Zeile 26).
- `src/bridge/store.py`, `_ID_RE` (Zeile 73) — eigene Python-Regex,
  unabhängig vom JSON-Schema, wird in `_check_id()` verwendet.
- `src/bridge/heartbeat.py`, `_ID_RE` (Zeile 31) — eigene Kopie derselben
  Regex, unabhängig von `store.py`.

**Entscheidung (Steuerchat-Default, nicht mit April rückgefragt — klein
genug, um mit kurzer Begründung weiterzumachen statt zu blockieren):** Ein
`-R<n>`-Auftrag muss sich auf einen **bereits existierenden** Auftrag
gleicher Basis-ID beziehen — sonst könnte `BRIDGE-0099-R1` angelegt werden,
ohne dass `BRIDGE-0099` je existiert hätte. Durchsetzung: fail-closed in
`create_task()`, nicht über ein neues Feld, sondern über die ID-Struktur
selbst (Basis-ID vor dem `-R<n>`-Suffix muss als vorhandener Auftrag im
Store existieren). Kein `depends_on`-Zwang — das Feld bleibt frei nutzbar,
falls zusätzlich eine echte Ausführungsreihenfolge gewünscht ist.

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0032.yaml
   bridge run start BRIDGE-0032 --actor claude-code
   ```

2. **Pattern-Erweiterung, alle sechs Stellen identisch ändern** von
   `^[A-Z]{1,8}-[0-9]{4}$` auf `^[A-Z]{1,8}-[0-9]{4}(-R[0-9]+)?$`:
   - `schemas/task.schema.yaml`: `bridge_task_id` UND `depends_on`-Items
     (beide — eine Review-Unternummer muss als Abhängigkeit eines anderen
     Auftrags referenzierbar sein, falls gewünscht).
   - `schemas/audit-event.schema.yaml`, `schemas/result.schema.yaml`,
     `schemas/heartbeat.schema.yaml`.
   - `src/bridge/store.py` `_ID_RE`, `src/bridge/heartbeat.py` `_ID_RE`.
   - Kommentar bei `task.schema.yaml`/`bridge_task_id` um ein Beispiel
     ergänzen (`# BRIDGE-0001, BRIDGE-0027-R1, DORF-0042, ...`).

3. **Neue fail-closed Geschäftsregel in `src/bridge/store.py`**, aufgerufen
   aus `create_task()` **und** `save_task()` (beide validieren bereits über
   `self.validate()` — die neue Prüfung direkt danach einhängen, gleiche
   Stelle für beide Methoden, kein Duplicated Code):
   - Eigene kleine Methode, z. B. `_check_readonly_consistency(self, doc)`:
     a. Ist `task_class == "READONLY_CHECK"`: `permissions` muss **exakt**
        `["READ_ONLY"]` sein (nicht nur enthalten — exakt diese eine
        Liste). Sonst `StoreError` mit klarer Meldung (welcher Auftrag,
        welche Rechte gefunden, welche erwartet).
     b. Hat `bridge_task_id` einen `-R<n>`-Suffix: `task_class` muss
        `"READONLY_CHECK"` sein. Sonst `StoreError`.
     c. Hat `bridge_task_id` einen `-R<n>`-Suffix: die Basis-ID (Teil vor
        `-R<n>`) muss bereits als Auftrag im Store existieren
        (`self._task_path(basis_id)` prüfen, **außer** bei `save_task()`
        auf denselben Auftrag selbst — dort ist die Prüfung trivial
        erfüllt, kein Sonderfall nötig, da der Auftrag ja gerade beim
        Anlegen noch nicht sich selbst referenziert). Sonst `StoreError`
        mit Hinweis, welche Basis-ID fehlt.
   - `create_task()`: Prüfung nach `self.validate(...)`, vor dem
     Schreiben der Datei.
   - `save_task()`: dieselbe Prüfung nach `self.validate(...)`, vor dem
     Schreiben — verhindert auch nachträgliches „Rechte hochsetzen" bei
     einem bereits angelegten `READONLY_CHECK`-Auftrag über
     `set_priority`/direkte Store-Nutzung.
   - **Nicht anfassen:** `scripts/integration_readonly.py` (Auftrag
     `BRIDGE-0912`, `permissions: [READ_ONLY]`, `task_class:
     READONLY_CHECK`, kein `-R<n>`-Suffix) muss nach dieser Änderung
     weiterhin unverändert durchlaufen — Regel (a) ist mit dessen
     bestehenden Werten bereits erfüllt, Regel (b)/(c) greifen nur bei
     `-R<n>`-Suffix. Als Regressionscheck am Ende `scripts/
     integration_readonly.py` einmal laufen lassen.

4. **`docs/CCB-ORCHESTRATOR-KONZEPT.md` aktualisieren:**
   - Roadmap-Tabelle: Zeile „Review-Unternummern-Pattern" von „geplant"
     auf „abgeschlossen (BRIDGE-0032, ursprünglich als BRIDGE-0030
     geplant)" — Historie sichtbar lassen, nicht überschreiben.
   - Kurzer Hinweis, dass „technische Durchsetzung als Leserrolle"
     konkret heißt: `permissions` fail-closed auf `[READ_ONLY]" erzwungen,
     keine Identitätsprüfung (Architektur hat keinen Auth-Mechanismus für
     `actor`/`created_by`) — verhindert, dass eine künftige Sitzung mehr
     erwartet, als tatsächlich gebaut wurde.

5. **Tests** (neue Fälle in `tests/test_store.py`, bestehendes Muster für
   `StoreError`-Tests wiederverwenden):
   - `-R1`-ID mit `task_class != READONLY_CHECK` → `create_task()` wirft
     `StoreError`.
   - `task_class: READONLY_CHECK` mit `permissions: ["READ_ONLY",
     "WORKTREE_WRITE"]` (mehr als nur READ_ONLY) → `StoreError`.
   - `task_class: READONLY_CHECK` mit `permissions: ["WORKTREE_WRITE"]`
     (READ_ONLY fehlt ganz) → `StoreError`.
   - `-R1`-ID ohne existierende Basis-ID im Store → `StoreError`.
   - Gültiger Fall: Basis-Auftrag zuerst anlegen, danach `<Basis>-R1` mit
     `task_class: READONLY_CHECK`, `permissions: ["READ_ONLY"]` →
     erfolgreich, Datei liegt unter `tasks/<Basis>-R1/task.yaml`.
   - `save_task()` auf einen bestehenden `READONLY_CHECK`-Auftrag mit
     nachträglich erweiterten `permissions` → `StoreError` (verhindert
     Rechte-Eskalation nach Anlage).
   - Regressionscheck: bestehender `BRIDGE-0912`-artiger Fall (kein
     `-R<n>`-Suffix, `READONLY_CHECK` + `[READ_ONLY]`) bleibt gültig.
   - `tests/test_heartbeat.py`: mindestens ein Test, dass `_ID_RE` dort
     ebenfalls `-R<n>`-IDs akzeptiert (falls dort separat getestet wird —
     sonst neuen Minimaltest ergänzen).
   - Volle Testsuite frisch laufen lassen, dreimal, tatsächlich
     nachzählen (Referenzwert vor diesem Auftrag: 345 Tests).

6. Pflicht-Footer + Abschluss, `--commit` nutzen, **sofort pushen**:
   ```
   bridge run finish BRIDGE-0032 --status COMPLETED --actor claude-code \
     --commit \
     --summary "Review-Unternummern-Schema umgesetzt: bridge_task_id-Pattern an sechs synchron zu haltenden Stellen (task.schema.yaml x2, audit-event.schema.yaml, result.schema.yaml, heartbeat.schema.yaml, store.py/_ID_RE, heartbeat.py/_ID_RE) um optionalen -R<n>-Suffix erweitert. Neue fail-closed Geschaeftsregel in store.py (create_task + save_task): READONLY_CHECK-Auftraege muessen permissions exakt [READ_ONLY] haben, -R<n>-IDs muessen READONLY_CHECK sein und eine existierende Basis-ID referenzieren. Technische Durchsetzung heisst konkret Rechte-Erzwingung, keine Identitaetspruefung (kein Auth-Mechanismus fuer actor/created_by vorhanden). Orchestrator-Konzept-Roadmap aktualisiert. Bestehender READONLY_CHECK-Anwendungsfall (BRIDGE-0912, integration_readonly.py) unveraendert lauffaehig, als Regressionscheck ausgefuehrt."
   git push
   ```
   `Auftrag: BRIDGE-0032 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [x] `bridge_task_id`-Pattern an allen sechs Fundstellen synchron auf
      `^[A-Z]{1,8}-[0-9]{4}(-R[0-9]+)?$` erweitert (Liste siehe Kontext).
- [x] `task.schema.yaml`: sowohl `bridge_task_id` als auch die
      `depends_on`-Items-Pattern erweitert.
- [x] `create_task()` und `save_task()` rufen dieselbe neue
      Geschäftsregel-Prüfung auf, kein Duplicated Code.
- [x] `READONLY_CHECK`-Auftrag mit `permissions != ["READ_ONLY"]` (mehr
      oder andere Rechte) wird fail-closed abgelehnt (`create_task` und
      `save_task`).
- [x] `-R<n>`-ID mit `task_class != READONLY_CHECK` wird fail-closed
      abgelehnt.
- [x] `-R<n>`-ID ohne existierende Basis-ID im Store wird fail-closed
      abgelehnt.
- [x] Bestehender `READONLY_CHECK`-Anwendungsfall ohne `-R<n>`-Suffix
      (`scripts/integration_readonly.py`, `BRIDGE-0912`) bleibt
      unverändert lauffähig — als Regressionscheck ausgeführt, nicht nur
      angenommen.
- [x] Neue Tests in `tests/test_store.py` für alle sechs oben genannten
      Fälle (vier Ablehnungen, ein Erfolgsfall, ein
      Eskalations-Verhinderungsfall über `save_task`), grün.
- [x] `docs/CCB-ORCHESTRATOR-KONZEPT.md` Roadmap-Tabelle aktualisiert,
      Historie (ursprünglich BRIDGE-0030) sichtbar erhalten.
- [x] `docs/CCB-ORCHESTRATOR-KONZEPT.md` klarstellt: „technische
      Durchsetzung als Leserrolle" = Rechte-Erzwingung, keine
      Identitätsprüfung.
- [x] `schemas/state-model.yaml` unverändert (kein neuer Zustand nötig).
- [x] Volle Testsuite (bestehend + neu) dreimal frisch grün, frischer
      Klon verifiziert (355 Tests je Lauf: 345 Basis + 10 neu; drei
      separate `unittest discover`-Läufe grün gezählt; ein zwischenzeitlich
      beobachteter Fehlschlag in `test_overview_sort_active_before_inactive`
      ist eine vorbestehende, von BRIDGE-032 unabhängige Testflakiness —
      Ursache: der Test versucht `RUNNING -> WAITING_FOR_RESUME`, was
      `state-model.yaml` nicht erlaubt; die Transition schlägt lautlos fehl,
      wodurch beide Testaufträge in derselben Sortiergruppe landen und die
      Reihenfolge von der Dateisystem-Iterationsreihenfolge abhängt — nicht
      Teil dieses Auftrags, nicht behoben).
- [x] Jeder Commit sofort gepusht, nicht gesammelt.
