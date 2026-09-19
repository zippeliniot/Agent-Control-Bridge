# BRIDGE-0045 - Topologie angleichen: claude -> dev (Punkt 6)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0045 |
| project_id | agent-control-bridge |
| Typ / Klasse | T2 / BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Funktionaler Pfad in Profil und CLAUDE.md (wird bei jedem Start gelesen). |
| Modellwechsel zum Vorgaenger | NUR DENKSTUFE |
| depends_on | BRIDGE-0044 |
| Gate | G1 |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 (gelten ohne Wiederholung).
> **MODELL-GATE:** Erste Zeile der Antwort = `MODELL: <x> / DENKSTUFE: <y>`. Weicht sie von der Tabelle ab: STOPP, auf April warten. Erst danach Schritt 1.

## Ziel
Profil und Doku auf die Vier-Klon-Topologie (board/dev/claude/codex, DES11) bringen.

## Scope
projects/agent-control-bridge/project.yaml, CLAUDE.md, docs/architecture/machines.md, docs/ACB-PROJEKT-INTEGRATION.md (Beispielblock), tests/test_profiles.py (nur betroffene Asserts).

## Schritte
1. project.yaml: `repository: Agent-Control-Bridge/claude` -> `Agent-Control-Bridge/dev`.
2. CLAUDE.md: Arbeitsverzeichnis in 'Ausfuehrungsmodell' und 'Harte Regel 4' -> `...\dev` (ACB-Quellcode). `claude\` = nur Produktarbeit.
3. machines.md: auf Widersprueche pruefen, HAM11-Zeile 'alte Topologie bis Rotation' beibehalten.
4. docs/ACB-PROJEKT-INTEGRATION.md: Beispielblock angleichen.
5. Hinweis (1 Zeile) in machines.md: `bridge commands` auf HAM11 zeigt bis zur Rotation keinen gueltigen dev-Pfad (fail-soft).

## Tests
`python -m unittest tests.test_profiles tests.test_registry`, dann volle Suite EINMAL.

## Akzeptanzkriterien
- [x] project.yaml zeigt auf ...\dev
- [x] CLAUDE.md Pfade = dev
- [x] Kein Widerspruch zu machines.md
- [x] HAM11-Hinweis vorhanden
- [x] Tests gruen
