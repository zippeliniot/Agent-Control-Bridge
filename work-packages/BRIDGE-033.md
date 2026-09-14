# BRIDGE-033 — Zwei Bugfixes: Work-Package-Whitelist-Mismatch (`--commit`) + flaky Sortiertest

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0033 |
| project_id | codex-control-bridge |
| task_class | BUGFIX |
| depends_on | (keine) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen) |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe LOW — beide Fixes sind mechanisch und vollständig spezifiziert: ein String-Formatierungsfehler in einer einzelnen Funktion, und eine falsche Zustandsübergangs-Sequenz in einem Test. Keine Entwurfsentscheidung, keine Mehrdeutigkeit. |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit`, und **sofort**, nicht gesammelt.
> - **Ironie am Rande:** Dieser Auftrag repariert genau den Mechanismus
>   (`--commit`-Whitelist), der die letzten zwei Läufe (BRIDGE-031,
>   BRIDGE-032) selbst betroffen hat. Solange Fix 1 nicht committet ist,
>   kann `run finish --commit` bei **diesem eigenen Auftrag** erneut am
>   selben Whitelist-Mismatch scheitern, wenn das Work-Package Checkbox-
>   Änderungen bekommt — das ist normal, nicht selbst nochmal als neuer
>   Bug melden. Fällt `--commit` am Ende dieses Laufs auf denselben
>   Mismatch, `git add work-packages/BRIDGE-033.md` manuell nachziehen
>   (wie bei BRIDGE-031/032), das ist erwartet und kein Fehlschlag des
>   Fixes selbst — der Fix wirkt erst ab dem **nächsten** Auftrag danach.

## Kontext

Bei der Vier-Punkte-Prüfung von BRIDGE-032 aufgefallen: Claude Codes eigene
Commit-Message „BRIDGE-0032 RUN-01: run finish COMPLETED (Whitelist-Mismatch
work-packages/BRIDGE-032.md vs. -0032.md manuell committet, wie bei
BRIDGE-031)" — **zum zweiten Mal in Folge** musste der Checkbox-Commit am
Ende eines Laufs manuell nachgezogen werden, weil `--commit` ihn ablehnt.

**Root Cause, im Code gelesen** (`src/bridge/gitops.py`,
`expected_git_files()`, Zeile 67):
```python
base.append(f"work-packages/{task_id}.md")
```
`task_id` ist die volle 4-stellige `bridge_task_id` (z. B. `BRIDGE-0032`) —
das ergibt `work-packages/BRIDGE-0032.md`. **Jede** tatsächlich existierende
Work-Package-Datei im Repo (`BRIDGE-001.md` … `BRIDGE-032.md`, 32 Dateien,
ausnahmslos) folgt aber der 3-stelligen Konvention **ohne** führende Null.
Die Whitelist prüft also gegen einen Dateinamen, der nie existiert — der
Checkbox-Commit am Laufende scheitert dadurch **systematisch**, nicht nur
gelegentlich.

**Bewusste Entscheidung, nicht zur Debatte gestellt:** Die 32 bestehenden
Dateien werden **nicht** umbenannt (Historie, Links, bisherige `git log`-
Referenzen bleiben unangetastet) — `gitops.py` wird an die tatsächliche,
etablierte Konvention angepasst, nicht umgekehrt.

**Zweiter, unabhängiger Fund**, ebenfalls bei der Vier-Punkte-Prüfung von
BRIDGE-032 aufgefallen (von Claude Code selbst schon sauber diagnostiziert
und im Work-Package vermerkt, hier nur übernommen und zum eigenen Auftrag
gemacht): `tests/test_cli.py`,
`test_overview_sort_active_before_inactive` versucht
`RUNNING -> WAITING_FOR_RESUME` direkt per CLI (`task set-status ...
WAITING_FOR_RESUME`). Laut `schemas/state-model.yaml`,
`allowed_transitions.RUNNING`, ist das **kein** gültiger Übergang (nur
`INTERRUPTED -> WAITING_FOR_RESUME` ist erlaubt) — der CLI-Aufruf schlägt
mit einem `TransitionError` fehl, der Rückgabewert wird im Test aber nicht
geprüft, der Fehlschlag bleibt unbemerkt. Der betroffene Auftrag
(`BRIDGE-0902`) bleibt dadurch in `RUNNING`, hat aber **kein**
Heartbeat-File — und `_overview_task_info()` behandelt „kein Heartbeat"
als „frisch"/aktiv (siehe Docstring: „oder kein HB = frisch"). Beide
Test-Aufträge landen dadurch in derselben Aktiv-Sortiergruppe, die
Reihenfolge zwischen ihnen hängt von der Dateisystem-Iterationsreihenfolge
ab — daher die beobachtete Flakiness, kein Produktionscode-Fehler, reines
Testproblem.

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0033.yaml
   bridge run start BRIDGE-0033 --actor claude-code
   ```

2. **Fix 1 — `src/bridge/gitops.py`:**
   - Neue kleine Hilfsfunktion, z. B. `_workpackage_filename(task_id: str)
     -> str`: zerlegt `task_id` in Präfix, 4-stellige Nummer und
     optionalen `-R<n>`-Suffix (Regex analog `_REVIEW_SUFFIX_RE` aus
     `store.py`, hier aber lokal/eigenständig — kein Cross-Import
     zwischen `gitops.py` und `store.py` nötig, beide Module sind
     unabhängig), formatiert die Nummer als `int(...)` mit
     **mindestens** 3 Stellen (`f"{int(nummer):03d}"` — kein starres
     Abschneiden auf 3 Stellen, funktioniert auch für vierstellige
     Nummern ab 1000, falls das Projekt je so weit kommt). Beispiel:
     `BRIDGE-0032` → `BRIDGE-032`, `BRIDGE-0027-R1` → `BRIDGE-027-R1`.
   - Zeile 67 nutzt diese Funktion statt des rohen `task_id`:
     `base.append(f"work-packages/{_workpackage_filename(task_id)}.md")`.

3. **Fix 2 — `tests/test_cli.py`,
   `test_overview_sort_active_before_inactive`:**
   - `BRIDGE-0902` über den gültigen Zwei-Schritt-Pfad in
     `WAITING_FOR_RESUME` bringen: `RUNNING -> INTERRUPTED` (mit Grund),
     dann `INTERRUPTED -> WAITING_FOR_RESUME` — beide Schritte einzeln
     per `self.cli(...)`.
   - **Beide** `self.cli(...)`-Aufrufe (und den bereits bestehenden für
     `BRIDGE-0901`) auf Erfolg prüfen (`code, _, err = self.cli(...);
     self.assertEqual(code, 0, err)`) — nicht nur den Rückgabewert
     verwerfen wie bisher. Das ist der eigentliche Kernfix: ein
     stillschweigend fehlschlagender Testaufbau darf nicht unbemerkt
     bleiben, unabhängig vom konkreten Übergang.

4. **Bestehende Tests in `tests/test_gitops.py` anpassen**, die den
   bisherigen (falschen) 4-stelligen Dateinamen erwarten — sonst bricht
   Fix 1 zwei bestehende Tests:
   - `test_run_finish_includes_results_and_workpackage`: Erwartung von
     `"work-packages/BRIDGE-0001.md"` auf `"work-packages/BRIDGE-001.md"`
     ändern.
   - `test_finish_webui_includes_results_and_workpackage`: dieselbe
     Änderung.
   - Neue Tests ergänzen: `_workpackage_filename()` direkt für einen
     `-R<n>`-Fall (`BRIDGE-0027-R1` → `BRIDGE-027-R1`) und für eine
     vierstellige Nummer ohne führende Nullen (`BRIDGE-1000` →
     `BRIDGE-1000`, falls sinnvoll simulierbar) — mindestens der
     `-R<n>`-Fall ist Pflicht, da BRIDGE-032 diese ID-Form neu eingeführt
     hat.

5. **Regressionscheck für Fix 1, real, nicht nur über Unit-Tests:** Nach
   dem Fix `bridge run finish` (oder den entsprechenden CLI-Pfad) einmal
   mit `--commit` gegen ein Szenario mit geänderter Work-Package-Datei
   laufen lassen (z. B. im Rahmen des eigenen Auftragsabschlusses, siehe
   Hinweis oben im Pflichtblock) und beobachten, ob die Whitelist jetzt
   greift — nicht nur behaupten, tatsächlich einmal durchlaufen lassen
   und das Ergebnis im Work-Package vermerken.

6. Volle Testsuite frisch laufen lassen, dreimal, tatsächlich nachzählen
   (Referenzwert vor diesem Auftrag: 355 Tests). Für `test_overview_
   sort_active_before_inactive` gezielt zusätzlich 5–10 Einzelwiederho-
   lungen (`python -m unittest tests.test_cli.<Klasse>.
   test_overview_sort_active_before_inactive` mehrfach) — die Flakiness
   war Reihenfolge-/Dateisystem-abhängig, ein einzelner grüner Lauf
   beweist den Fix nicht zuverlässig.

7. Pflicht-Footer + Abschluss, `--commit` nutzen (siehe Hinweis im
   Pflichtblock zum möglichen Whitelist-Mismatch bei diesem einen letzten
   Mal), **sofort pushen**:
   ```
   bridge run finish BRIDGE-0033 --status COMPLETED --actor claude-code \
     --commit \
     --summary "Zwei Bugfixes: (1) gitops.py expected_git_files() erwartete die volle 4-stellige bridge_task_id im Work-Package-Dateinamen (work-packages/BRIDGE-0032.md), tatsaechliche Konvention ist 3-stellig ohne fuehrende Null (work-packages/BRIDGE-032.md) - neue Hilfsfunktion _workpackage_filename() korrigiert das, verhindert den Whitelist-Mismatch der --commit bei BRIDGE-031/032 zum manuellen Nacharbeiten zwang. Bestehende Tests in test_gitops.py an die korrigierte Erwartung angepasst. (2) test_overview_sort_active_before_inactive versuchte einen ungueltigen RUNNING->WAITING_FOR_RESUME-Uebergang (laut state-model.yaml nur ueber INTERRUPTED erlaubt), der CLI-Aufruf schlug unbemerkt fehl (Rueckgabewert nicht geprueft), wodurch beide Testauftraege in derselben Sortiergruppe landeten - Testaufbau auf den gueltigen Zwei-Schritt-Pfad korrigiert, alle CLI-Aufrufe im Test pruefen jetzt ihren Exit-Code. Kein Produktionscode-Fehler bei Fix 2, reines Testproblem."
   git push
   ```
   `Auftrag: BRIDGE-0033 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [x] `gitops.py`: neue Hilfsfunktion konvertiert `bridge_task_id` korrekt
      in den etablierten Work-Package-Dateinamen (3-stellig, führende
      Null entfernt, `-R<n>`-Suffix erhalten, robust auch für ≥1000).
- [x] `expected_git_files()` nutzt diese Funktion für den
      `work-packages/`-Whitelist-Eintrag statt des rohen `task_id`.
- [x] Bestehende 32 Work-Package-Dateien **nicht** umbenannt.
- [x] `test_gitops.py`: beide betroffenen bestehenden Tests korrigiert,
      mindestens ein neuer Test für den `-R<n>`-Fall.
- [x] `test_overview_sort_active_before_inactive`: nutzt den gültigen
      `RUNNING -> INTERRUPTED -> WAITING_FOR_RESUME`-Pfad.
- [x] Alle `self.cli(...)`-Aufrufe in diesem Test prüfen ihren Exit-Code.
- [x] Test mehrfach einzeln wiederholt (5–10×) durchgängig grün, nicht
      nur einmal im Gesamtlauf (10/10 Einzelläufe grün).
- [ ] Realer Regressionscheck von Fix 1 durchgeführt (nicht nur Unit-Test
      behauptet) und im Work-Package dokumentiert.
- [x] Volle Testsuite (bestehend + angepasst) dreimal frisch grün,
      frischer Klon verifiziert (359 Tests je Lauf: 355 Basis + 4 neu;
      drei separate `unittest discover`-Läufe grün gezählt, inkl. der
      zuvor flakigen `test_overview_sort_active_before_inactive`).
- [x] Jeder Commit sofort gepusht, nicht gesammelt (Ausnahme siehe
      Hinweis im Pflichtblock zu diesem einen letzten möglichen
      Whitelist-Mismatch).
