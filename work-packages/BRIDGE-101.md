# BRIDGE-0101: ISSUE-0005 - push_mode-Durchsetzung + projektbezogene changed_files/base_head

| Feld | Wert |
|---|---|
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - T2 sicherheitsrelevant (Push-/Write-Gating), aber entlang bereits dokumentierten Sollverhaltens (CLAUDE.md Draft-Modus), kein offener Entwurf. |
| Modellwechsel zum Vorgaenger | NEIN (Vorgaenger BRIDGE-0100: Claude Sonnet 5 / LOW, BUGFIX) |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `src/bridge/cli.py`, `src/bridge/importer.py`, `projects/agent-control-bridge/project.yaml`, `tests/test_cli.py`, `tests/test_importer.py`, `tests/test_profiles.py` |

## Anlass

ISSUE-0005 (OPEN, Steuerchat 09.10.2026): `push_mode` steht bei keinem der
sieben Projekte auf `draft` (M1 Single-Writer nicht aktiv); der gemeinsame
ACB-Store-Branch (`main`) erlaubt dadurch Commit-Races zwischen gleichzeitig
laufenden Steuerchats verschiedener Projekte - real beobachtet bei
BRIDGE-0091 (Wetter-Steuerchat-Commits `a2600a4`/`22b4233` zogen sich in
`changed_files`/`base_head` eines anderen Projekts hinein).

**Pruefung gegen echten Code (Steuerchat, 09.10.2026, HEAD `c9e459a`):**
`profiles.get_push_mode()` (`src/bridge/profiles.py:150`) wird im gesamten
`src/bridge/` **nirgends** aufgerufen - weder in `cli.py` noch `runner.py`
noch `state_machine.py`. `push_mode: draft` ist damit heute ein gelesenes,
aber nirgends durchgesetztes Feld. `CLAUDE.md` Abschnitt "Draft-Modus"
beschreibt bereits das Soll-Verhalten (kein `task create`/`run start`/
`run finish`/Direkt-Write unter `tasks/`, `results/`, `audit/` bei
`push_mode: draft` - nur `bridge draft write`), **ist aber nicht im Code
abgebildet.** `test_stage_a.py` (G2-Nachweis) prueft nur, dass der separate
Draft-/Import-Mechanismus selbst funktioniert, nicht dass `push_mode: draft`
automatisch dorthin umleitet.

April (Steuerchat, 09.10.2026): Option A (push_mode) und Option B
(`changed_files`/`base_head` projektbezogen) werden zusammengelegt, da beide
dieselben CLI-Funktionen beruehren.

## Teil A - push_mode-Durchsetzung

`src/bridge/cli.py`: `task create`, `run start`, `run finish`,
`task copied`, `task archive` laden das Projektprofil
(`profiles.load_profile`) zum jeweiligen `project_id` und lehnen fail-closed
ab, wenn `profiles.get_push_mode(profile) == "draft"` - mit Fehlermeldung,
die auf `bridge draft write`/`bridge task import` verweist (CLAUDE.md
Draft-Modus, bereits dokumentiertes Soll-Verhalten, hier erstmals
durchgesetzt). `--commit` darf die Store-Aktion in diesem Fall nicht
ausfuehren.

Danach `projects/agent-control-bridge/project.yaml`: `push_mode: draft`
setzen (erstes Projekt, hoechste Steuerchat-Parallelitaet, von April
bestaetigt).

## Teil B - projektbezogene changed_files/base_head

`src/bridge/importer.collect_git_info()` (Zeile ~99): `git diff --name-only
base_head HEAD` laeuft aktuell repo-weit. Auf den `task_prefix` des
jeweiligen `project_id` einschraenken: nur Pfade unter `tasks/<prefix>-*`,
`results/<prefix>-*`, `work-packages/<prefix>-*.md`,
`open-issues/<project_id>/` in `changed_files` aufnehmen; Pfade anderer
Projekte aus dem Rohdiff herausfiltern, nicht nur zusaetzlich auflisten.

**Bewusste Abgrenzung (nicht geloest, hier dokumentiert statt stillschweigend
ausgelassen):** `audit/audit.jsonl` ist eine einzige, von allen Projekten
gemeinsam genutzte Append-only-Datei - pfadbasiertes Filtern kann sie nicht
einem Projekt zuordnen, sie erscheint also weiterhin in jedem
`changed_files` mit, sobald im Diff-Bereich irgendein Audit-Eintrag
hinzukam, unabhaengig vom Projekt. Das ist keine Regression gegenueber heute
(heute ist das Problem nur groesser), aber auch keine vollstaendige Loesung
von ISSUE-0005 fuer diese eine Datei. Falls das in der Praxis noch stoert:
eigenes Folge-Issue, nicht Teil dieses Auftrags (Inhalts-/Zeilenbasiertes
Filtern nach `bridge_task_id`-Praefix waere eine eigene, groessere
Aenderung).

## Akzeptanzkriterien

- [x] `task create`/`run start`/`run finish`/`task copied`/`task archive`
  lehnen bei `push_mode: draft` fail-closed ab, Fehlermeldung verweist auf
  `bridge draft write`
- [x] Bei `push_mode: direct` (Default, alle anderen sechs Projekte)
  unveraendertes Verhalten - Regressionstest
- [x] `projects/agent-control-bridge/project.yaml` auf `push_mode: draft`
  umgestellt
- [x] `collect_git_info()` liefert `changed_files` nur fuer Pfade des
  eigenen `task_prefix` (+ `open-issues/<project_id>/`), Pfade anderer
  Projekte im selben Diff-Bereich werden herausgefiltert - neuer Test mit
  gemischtem Diff (zwei Projekte im selben `base_head..HEAD`-Bereich)
- [x] `audit/audit.jsonl`-Einschraenkung bewusst nicht umgesetzt, im Code-
  Kommentar und in diesem WP begruendet (siehe oben), nicht stillschweigend
  weggelassen
- [x] Volle Suite gruen (594 Bestand + neue Tests)
