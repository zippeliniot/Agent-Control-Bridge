# BRIDGE-035 — `integration_readonly.py` projektparametrisierbar machen + Pre-Flight-Head-Check

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0035 |
| project_id | codex-control-bridge |
| task_class | FEATURE |
| depends_on | (keine) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen) |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe LOW — neue optionale CLI-Argumente mit vollständiger Rückwärtskompatibilität (Defaults reproduzieren exakt das bisherige CCB-Selbstcheck-Verhalten), ein zusätzlicher fail-closed Vergleich nach vorhandenem Muster. Keine Architekturänderung, kein neuer Zustand. |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit`, und **sofort**, nicht gesammelt.
> - **Kein Zugriff auf das echte Dorfschaft-Repository** — dieser Auftrag
>   ändert nur `scripts/integration_readonly.py` und seine Tests, getestet
>   ausschließlich gegen synthetische Temp-Repos (bestehendes Testmuster).

## Kontext

Reaktion auf eine zweite Bereitschaftsprüfung von ChatGPT — dort korrekt
bemängelt: `scripts/integration_readonly.py` (BRIDGE-012) ist „nicht wirklich
projektparametrisierbar". Nachgeprüft (Verifikationspflicht Nr. 3, echten
Code gelesen, nicht die Doku):

- `--target`/`--out`/`--task-id` sind bereits vorhanden und funktionieren
  gegen ein beliebiges Git-Repo.
- **Aber:** In `run()` wird das an `ReadOnlyProjectAdapter` übergebene
  synthetische Profil hartkodiert mit `project_id: "codex-control-bridge"`,
  `task_prefix: "BRIDGE"`, `default_branch: "main"` gebaut — unabhängig
  vom tatsächlichen `--target`. Bei einer künftigen Beobachtung von
  Dorfschaft würde das erzeugte `result.yaml` fälschlich
  `codex-control-bridge` als `project_id` tragen — irreführende Provenienz,
  kein Absturz, aber falsche Daten.
- **Kein Pre-Flight-Vergleich gegen einen erwarteten Branch/HEAD.** Das
  Skript beweist nur „HEAD vorher == HEAD nachher" (Selbstkonsistenz) —
  nicht, dass vorher überhaupt der **richtige** Commit/Branch beobachtet
  wurde. Zeigt versehentlich auf den falschen Branch/Checkout, „passt" das
  Skript trotzdem, solange sich während der Beobachtung nichts ändert.

**Bewusste Abgrenzung, aus der vorherigen fachlichen Bewertung
übernommen** (siehe vorheriger Steuerchat-Vergleich zu ChatGPTs vollem
Anforderungskatalog): Dieser Auftrag baut **keinen** Linux-Executor-Dienst,
**keinen** API-/MCP-Adapter, **keine** Auftragsreservierung/Locking, **keine**
Identitätsverifikation. Nur die zwei oben genannten, konkret verifizierten
Lücken — das genügt, damit ein späterer, von einem Menschen begleiteter
`DORF-*`-Pilotauftrag nicht an vermeidbaren, vorab bekannten Fehlern
scheitert. Der reale WSL-Worktree-Pfad wird **nicht** gebraucht — alle
neuen Argumente werden vom **Aufrufer** des Skripts gesetzt (also erst beim
tatsächlichen Pilotauftrag selbst), nicht von diesem Auftrag vorgegeben.

**Platzierungsentscheidung (eigener, kleiner Fix statt größerem Umbau):**
Der Pre-Flight-Head-Check lebt **im Skript selbst** (`run()`, direkt nach
`before = _snapshot(target)`), **nicht** im gemeinsam genutzten
`adapter.py` — der Adapter wird auch von anderer Stelle verwendet
(`ReadOnlyProjectAdapter` selbst bleibt unverändert), ein Vergleich gegen
einen *erwarteten* Head ist eine Eigenschaft dieses spezifischen
Integrationstest-Skripts, nicht des generischen Adapters.

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0035.yaml
   bridge run start BRIDGE-0035 --actor claude-code
   ```

2. **`scripts/integration_readonly.py`, neue optionale CLI-Argumente**
   (alle mit Default, der das bisherige Verhalten exakt reproduziert —
   bestehende Aufrufe ohne die neuen Flags dürfen sich nicht ändern):
   - `--project-id` (Default: `"codex-control-bridge"`).
   - `--task-prefix` (Default: `"BRIDGE"`).
   - `--expected-branch` (Default: `None` — nur informativ, kein Abbruch
     bei fehlendem Wert; falls gesetzt, in den Report/die Ausgabe
     aufnehmen, aber `git_info["branch"]` wird bereits vom Adapter
     ermittelt — kein Zwang, hier zu vergleichen, außer es liegt sich
     trivial an).
   - `--expected-head` (Default: `None`). Ist gesetzt: direkt nach
     `before = _snapshot(target)` prüfen, ob `before["head"]` mit
     `--expected-head` übereinstimmt (Präfix-Vergleich zulassen, kurze
     und lange SHA sollen beide funktionieren — `before["head"].startswith
     (args.expected_head)`). Bei Abweichung: `RuntimeError` mit Klartext
     (erwarteter vs. tatsächlicher HEAD) — von `main()`s bestehendem
     `except Exception`-Fail-Closed-Pfad abgefangen, Exit 1, kein
     Sonderfall nötig.
   - `run()`-Signatur entsprechend erweitern (neue Parameter mit
     Defaults, Aufrufreihenfolge/bestehende Positionsargumente nicht
     brechen — Keyword-Argumente verwenden).

3. **`_observation_task()` und das synthetische Profil in `run()`**
   nutzen jetzt `args`/Parameter statt hartkodierter Werte: `project_id`,
   `task_prefix` (fürs Profil), `default_branch` (aus `--expected-branch`
   falls gesetzt, sonst weiterhin `"main"` als Fallback wie bisher).

4. **`checks`-Dict um `head_matches_expected` ergänzen**, wenn
   `--expected-head` gesetzt war (sonst diesen Key weglassen, nicht mit
   `True` auffüllen — ein nicht angefordertes Kriterium ist kein
   bestandenes Kriterium).

5. **Tests in `tests/test_integration_readonly.py`** (bestehendes Muster
   mit synthetischem Temp-Git-Repo wiederverwenden):
   - Neue Argumente unbenutzt → Verhalten identisch zu vorher
     (Regressionscheck, exakt die bestehenden vier Tests bleiben grün
     ohne inhaltliche Änderung).
   - `--project-id`/`--task-prefix` gesetzt → `result.yaml` im `--out`
     trägt die neuen Werte, nicht mehr `codex-control-bridge`/`BRIDGE`.
   - `--expected-head` korrekt (entspricht dem echten HEAD des
     synthetischen Repos) → `PASS`, `head_matches_expected: true` im
     Report.
   - `--expected-head` falsch gesetzt → `FAIL`, Exit-Code 1, klare
     Fehlermeldung mit beiden Head-Werten.
   - `--expected-head` als Kurz-SHA (7 Zeichen) gegen vollen HEAD → wird
     akzeptiert (Präfix-Vergleich).

6. **`docs/CCB-PROJEKT-INTEGRATION.md`/`README.md`** (Abschnitt
   „Read-only-Integrationstest (BRIDGE-012)"): die neuen Argumente kurz
   dokumentieren — ein bis zwei Sätze, kein neuer Abschnitt nötig.

7. Volle Testsuite frisch laufen lassen, dreimal, tatsächlich nachzählen
   (Referenzwert vor diesem Auftrag: 359 Tests).

8. Pflicht-Footer + Abschluss, `--commit` nutzen, **sofort pushen**:
   ```
   bridge run finish BRIDGE-0035 --status COMPLETED --actor claude-code \
     --commit \
     --summary "scripts/integration_readonly.py projektparametrisierbar gemacht: neue optionale Argumente --project-id/--task-prefix/--expected-branch/--expected-head, vollstaendig rueckwaertskompatibel (Default reproduziert exakt das bisherige CCB-Selbstcheck-Verhalten). Bisher hartkodiertes Profil (project_id/task_prefix/default_branch immer codex-control-bridge/BRIDGE/main unabhaengig vom Ziel) korrigiert - verhindert irrefuehrende Provenienz bei einer spaeteren Beobachtung eines fremden Repos (z.B. Dorfschaft). Neuer Pre-Flight-Check: --expected-head wird vor der Beobachtung gegen den tatsaechlichen HEAD geprueft, fail-closed bei Abweichung (Praefix-Vergleich, kurze und lange SHA). Kein Linux-Executor-Dienst, kein API-Adapter, kein Locking, keine Identitaetsverifikation - bewusst nicht Teil dieses Auftrags, siehe Kontext im Work-Package."
   git push
   ```
   `Auftrag: BRIDGE-0035 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [ ] Neue optionale Argumente `--project-id`, `--task-prefix`,
      `--expected-branch`, `--expected-head`, alle mit Default = bisheriges
      Verhalten.
- [ ] `_observation_task()` und das synthetische Adapter-Profil nutzen die
      übergebenen Werte statt hartkodierter `codex-control-bridge`/
      `BRIDGE`/`main`.
- [ ] `--expected-head` gesetzt und abweichend → `RuntimeError`, Skript
      beendet mit Exit 1, Fehlermeldung nennt beide Head-Werte.
- [ ] `--expected-head` als Kurz-SHA wird per Präfix-Vergleich akzeptiert.
- [ ] `checks["head_matches_expected"]` nur vorhanden, wenn
      `--expected-head` gesetzt war.
- [ ] Bestehende vier Tests in `test_integration_readonly.py` bleiben ohne
      inhaltliche Anpassung grün (reiner Regressionscheck).
- [ ] Mindestens vier neue Tests (siehe Umsetzungsschritt 5), grün.
- [ ] `docs/CCB-PROJEKT-INTEGRATION.md`/`README.md` kurz aktualisiert.
- [ ] Kein Zugriff auf das echte Dorfschaft-Repository in diesem Auftrag.
- [ ] Volle Testsuite (bestehend + neu) dreimal frisch grün, frischer
      Klon verifiziert.
- [ ] Jeder Commit sofort gepusht, nicht gesammelt.
