# BRIDGE-0104: wp-lint.py (BRIDGE-0102) um drei Pruefungen erweitern

| Feld | Wert |
|---|---|
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_COMMIT, GIT_PUSH |
| Scope | `scripts/wp-lint.py`, `tests/test_wp_lint.py`, `work-packages/BRIDGE-104.md` |

## Anlass

`scripts/wp-lint.py` (BRIDGE-0102) prueft seit dessen Umsetzung vier Dinge
vor jeder Uebergabe eines WP+Staging-YAML-Paars: Modell/Denkstufe-Zeile im
WP-Kopf vorhanden und gueltig, Staging-YAML schema-valide mit nichtleerem
`model`/`reasoning_level`, Modell/Denkstufe-Uebereinstimmung WP↔YAML,
`bridge_task_id` der YAML kommt in der WP-Ueberschrift vor.

`ISSUE-0006` (Steuerchat 09.10.2026) deckte ein verwandtes, bisher nicht
mechanisch geprueftes Muster auf: `BRIDGE-0092` wurde an drei Stellen im
Repo (Uebergabedatei, OpenIssue-Notiz, ein anderes WP) als abgeschlossener
Auftrag zitiert, obwohl nie ein formaler `tasks/BRIDGE-0092/task.yaml`
angelegt wurde. Entscheidung damals: keine rueckwirkende Nachbuchung, das
Issue dokumentiert die Luecke nur abschliessend. BRIDGE-0104 generalisiert
dieses Muster als automatische Pruefung, statt es bei jedem Einzelfall
erneut manuell zu entdecken.

Zusaetzlich faellt bei der Durchsicht der elf WPs BRIDGE-090 bis BRIDGE-0103
auf: Issue-Referenzen (`ISSUE-NNNN`) im WP-Text werden nirgends gegen die
tatsaechlich existierenden Dateien unter `open-issues/<project_id>/`
geprueft, und eine fehlende `## Akzeptanzkriterien`-Sektion oder ein
fehlender Scope-Hinweis in der Kopftabelle wuerde bisher nicht erkannt,
obwohl beides fuer das Checkpoint-Register (`CLAUDE.md`, Abschnitt
„Checkpoint & Resume", Punkt 2) vorausgesetzt wird.

## Entscheidung zum Umfang (bewusste Abgrenzung)

- **Keine `decision_id`-Referenzpruefung.** Es existiert noch kein
  Decision-Log-Store (das ist der offene Punkt B in der Reihenfolge
  E→F→B→A→C→D), gegen den eine solche Referenz geprueft werden koennte.
- **Keine Pruefung von Uebergabedateien** (`docs/handover/ACB-UEBERGABE-v*.md`)
  gegen den Qualitaetsrahmen aus BRIDGE-0103 — andere Dateiklasse mit
  eigenem Format, nicht Gegenstand dieses WP.

## Ergebnisvertrag

`scripts/wp-lint.py` um drei weitere Pruefungen erweitern (zusaetzlich zu
den bestehenden vier aus BRIDGE-0102, die unveraendert bleiben):

**5. Issue-Referenzen aufloesbar.** Jedes Vorkommen von `ISSUE-NNNN`
(vierstellig) im WP-Text wird gegen
`open-issues/<project_id>/<project_id>-ISSUE-NNNN.yaml` geprueft
(`project_id` aus der Staging-YAML). Existiert die Datei nicht →
**Fehler, Exit 1.**

> **Offene Entscheidung fuer April:** Die v25-Uebergabe nennt fuer diese
> Pruefung keinen Exit-Code, anders als bei Pruefung 6 unten, wo explizit
> „Warnung, Exit bleibt 0" steht. Dieser Entwurf setzt **Fehler/Exit 1** an,
> weil Fail-closed hier der Repo-Default ist (vgl. BRIDGE-0102-Anlass:
> „Durchsetzung statt Erinnerung") und eine nicht aufloesbare Referenz
> typischerweise ein Tippfehler/eine Verwechslung ist (siehe die
> `ISSUE-0004`-Doppelvergabe in `ACB-UEBERGABE-v22.md` §1a). Bitte vor
> Auslieferung an Claude Code bestaetigen oder korrigieren.

**6. BRIDGE-Referenz + Abschlusswort ohne `task.yaml` (ISSUE-0006-Muster
generalisiert).** Jedes Vorkommen von `BRIDGE-NNNN` im WP-Text, das im
selben Satz/derselben Zeile mit einem der Abschlusswoerter `ARCHIVED` oder
`COMPLETED` auftritt (die beiden Terminalzustaende aus
`schemas/task.schema.yaml`), wird gegen `tasks/<id>/task.yaml` geprueft
(ID normalisiert auf vierstelliges Format `BRIDGE-0NNN`). Fehlt die Datei
→ **Warnung auf stderr, Exit bleibt 0.**

**7. Fehlende `## Akzeptanzkriterien`-Sektion oder fehlender Scope-Hinweis.**
Der WP-Koerper muss eine Ueberschrift `## Akzeptanzkriterien` enthalten,
UND die Kopftabelle muss eine Zeile `Scope` mit nichtleerem Wert enthalten.
Trifft eines von beiden nicht zu → **Fehler, Exit 1.**

Bei jedem Verstoss: genau benannte Fehler-/Warnmeldung auf stderr
(Datei+Zeile wo moeglich), wie bei den bestehenden vier Pruefungen.

## Akzeptanzkriterien

- [x] Pruefung 5: WP mit einer frei erfundenen, nicht existierenden
  ISSUE-Referenz wird abgelehnt (Exit 1, konkrete Fehlermeldung)
- [x] Pruefung 5: WP mit einer tatsaechlich existierenden ISSUE-Referenz
  (z. B. `ISSUE-0006`) wird akzeptiert
- [x] Pruefung 6: WP mit `BRIDGE-Referenz` + Abschlusswort ohne
  zugehoeriges `task.yaml` erzeugt eine Warnung auf stderr, Exit bleibt 0
  (Regressionstest analog dem `BRIDGE-0092`/`ISSUE-0006`-Fall)
- [x] Pruefung 6: WP mit `BRIDGE-Referenz` + Abschlusswort UND
  existierendem `task.yaml` erzeugt keine Warnung
- [x] Pruefung 7: WP ohne `## Akzeptanzkriterien`-Sektion wird abgelehnt,
  Exit 1
- [x] Pruefung 7: WP ohne (oder mit leerer) `Scope`-Zeile in der
  Kopftabelle wird abgelehnt, Exit 1
- [x] Die bestehenden vier Pruefungen aus BRIDGE-0102 bleiben unveraendert
  gruen (volle Regressionssuite)
- [x] `tests/test_wp_lint.py` um Tests fuer alle drei neuen Pruefungen
  erweitert
- [x] Volle Suite gruen
