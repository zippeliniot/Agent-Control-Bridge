# BRIDGE-0080 - Web-UI Projekt-Spalte vereinheitlichen (task_prefix statt roher project_id)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0080 |
| project_id | agent-control-bridge |
| Typ / Klasse | Einzelauftrag / FIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / LOW** - verifizierter Ein-Zeilen-Fix, bestehendes Vorbild (`cli.py:601`), keine neue Logik. |
| depends_on | BRIDGE-0079 (ARCHIVED) |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION |

> Ablauf: `/acb-auftrag BRIDGE-0080`. Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Ein Teil (A), kein Bündel.**

## Auftrag

**Befund (verifiziert gegen echten Code, 06.10.2026):** `webui.py::board_payload()` zeigt in der
"Alle Projekte - Gesamtuebersicht" (`_board_rows`, ueber `cli.py`) bereits den `task_prefix` via
`_board_project(store, task)` (`cli.py:601`, Fail-soft auf rohe `project_id` bei fehlendem/ungueltigem
Profil). Die separate Liste "Offene Auftraege ausserhalb des Boards" (derselbe `board_payload()`,
`webui.py:157`) nutzt stattdessen direkt `task.get("project_id", "?")` - unversioniert, inkonsistent
zur ersten Liste. **April-Entscheidung (06.10.2026):** beide Tabellen auf `task_prefix` vereinheitlichen.

**Ziel:** `webui.py:157` auf `_board_project(store, task)` umstellen - dieselbe Funktion, dasselbe
Fail-soft-Verhalten wie in der Board-Ansicht, keine neue Logik.

### Teil A - Projekt-Spalte in `board_payload()`'s `other`-Liste umstellen

**Scope:** `src/bridge/webui.py`, `tests/test_webui.py`.

1. `webui.py` Import-Liste aus `bridge.cli` (Zeile ~50) um `_board_project` erweitern.
2. `webui.py:157`: `"projekt": task.get("project_id", "?"),` ersetzen durch
   `"projekt": _board_project(store, task),`.
3. Test analog zu `tests/test_cli.py::test_board_uses_task_prefix_when_profile_present` (Profil-Fixture
   `projects/<id>/project.yaml` mit `task_prefix` im `tmp`-Store anlegen), aber gegen
   `GET /api/board` -> `data["other"]` statt gegen `bridge board`-Textausgabe.

**Tests:** `python -m unittest tests.test_webui`, dann volle Suite EINMAL, nur letzte 3 Zeilen zeigen.
- [x] `_board_project` importiert und in `webui.py:157` verwendet
- [x] Test belegt: `other`-Zeile zeigt `task_prefix` (z. B. `BRIDGE`) statt roher `project_id`, wenn Profil
      vorhanden; Fail-soft auf rohe `project_id` bleibt erhalten, wenn kein Profil existiert (bestehendes
      Verhalten, nicht neu zu testen, nur nicht brechen)

## Abschluss

1. Volle Suite EINMAL, nur die letzten 3 Zeilen zeigen.
2. `git status` sauber, dann Abschluss wie im Slash-Befehl.
- [ ] Volle Suite gruen
