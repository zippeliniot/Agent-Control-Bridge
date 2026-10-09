# BRIDGE-0095: Live-HEAD-Durchsetzung fuer base_head (ISSUE-0003, Teilbefund 2)

| Feld | Wert |
|---|---|
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `src/bridge/importer.py`, `tests/test_importer.py` |

## Anlass

ISSUE-0003 (OPEN seit 08.10.2026) hat zwei Teilbefunde. BRIDGE-0092 behob den ersten
(`--commit`-Flag fuer `bridge issue open/close`). Dieser Auftrag behebt den zweiten:
`expected_head`/`base_head` werden bisher ungeprueft als Vergleichsbasis fuer
`changed_files` verwendet - kein Abgleich gegen den tatsaechlichen, aktuellen HEAD. Real
belegter Schaden (KONZEPT-PRUEFRUNDEN-INTEGRATION_V3.md Abschnitt 4): BRIDGE-0089 trug
`base_head: 815ec26` statt des echten Git-Parents `c01c5b4`.

## Entscheidung zum Umfang (bewusste Abgrenzung)

Die urspruengliche Befundformulierung nennt drei vermischte Zeitpunkte (Auftragsbasis,
realer Git-Parent der Auftragsanlage, Vergleichsbasis fuer `changed_files`). Eine echte
Trennung in drei Schema-Felder waere eine eigene Schema-Governance-Frage (neues/geaendertes
Feld in `task.schema.yaml:100-115`, betrifft alle bestehenden `task.yaml`-Dokumente) und
wird hier **nicht** mitgezogen - konsistent mit der bereits in BRIDGE-0092 getroffenen
Abgrenzung ("riskanterer Eingriff, eigener Auftrag"). Stattdessen: der tatsaechlich
schadenstraechtige Teil - ein falscher/veralteter `base_head` wird stillschweigend als
Vergleichsbasis akzeptiert - wird durch eine harte Vorfahr-Pruefung geschlossen.

## Ergebnis

`importer.collect_git_info()` prueft jetzt vor der Diff-Bildung
(`git merge-base --is-ancestor <base_head> <HEAD>`); ist `base_head` kein Vorfahr des
aktuellen HEAD, schlaegt der Aufruf fail-closed mit `ImporterError` fehl, statt einen
Diff gegen einen unbezogenen Commit zu liefern. Neuer Helfer `_is_ancestor()`, bewusst
nicht ueber `_git()` (dessen generischer Non-Zero-Fehler wuerde rc=1 - der haeufigste,
erwartete "kein Vorfahr"-Fall - faelschlich als Git-Fehler behandeln).

## Akzeptanzkriterien

- [x] `collect_git_info()` lehnt einen `base_head` ab, der kein Vorfahr von HEAD ist
- [x] Bestehender Regressionstest (`test_base_head_auto_derived_from_task_yaml`,
  BRIDGE-023/024) bleibt gruen - echte Vorfahr-Beziehung im Testfall unveraendert
- [x] Neue Tests: Vorfahr-Fall (gruen), Seitenzweig (Ablehnung), unbekannter SHA
  (Ablehnung), `_is_ancestor()` direkt
- [x] Volle Suite gruen (581/581 - 577 Bestand + 4 neu)
- [x] Scope-Abgrenzung (keine Schema-Aenderung) explizit begruendet, nicht nur
  stillschweigend weggelassen
