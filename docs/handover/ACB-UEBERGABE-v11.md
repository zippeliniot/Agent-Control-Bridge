# ACB-Übergabe v11

Stand: HEAD `1a3c74b`, Repo `zippeliniot/Agent-Control-Bridge`. Letzter
archivierter Auftrag: **BRIDGE-0038**. Kein Auftrag aktuell `RUNNING`.

---

## 0. Was hat sich geändert (zuerst lesen)

**Reine Verifikations-/Übergabe-Sitzung** — keine neuen Aufträge erzeugt,
keine Code-Änderung durch den Steuerchat. Gegenüber v10 (Stand HEAD
`e328975`) hat sich Folgendes real geändert:

- **BRIDGE-0035** (Integrations-Skript `scripts/integration_readonly.py`
  projektparametrisierbar gemacht + Pre-Flight-Head-Check ergänzt) —
  **abgeschlossen und archiviert.** Alle 11 Akzeptanzkriterien im
  Arbeitspaket abgehakt, u. a. `--project-id`/`--task-prefix`/
  `--expected-head`-Argumente, Kurz-SHA-Präfixvergleich, vier neue Tests,
  bestehende vier Tests unverändert grün, keinerlei Zugriff auf das
  echte Dorfschaft-Repository.
- **BRIDGE-0038** (periodisches Auto-`git pull` für den Web-UI-Server) —
  **abgeschlossen und archiviert.** Alle 10 Akzeptanzkriterien abgehakt:
  `git_pull()` in `gitops.py` (Fast-Forward, fail-soft), Hintergrund-
  Thread mit sauberem Stopp, `--pull-interval` (Default 30s, `0`
  deaktiviert), gemeinsames `threading.Lock` mit den bestehenden
  Aktions-Endpunkten, Konsolen-Startmeldung, Hilfetext korrigiert (Web-UI
  ist nicht mehr fälschlich als „rein lesend" beschrieben), neue Tests
  für `git_pull()` (Erfolg + Konfliktfall).
- **Testsuite frisch verifiziert** (neues `.venv`, `pip install -r
  requirements.txt`, `python -m unittest discover -s tests`): **381
  Tests, alle grün.** Ein Log-Eintrag „Auto-Pull fehlgeschlagen:
  simulierter Absturz" während des Laufs ist erwarteter Testoutput
  (Konfliktfall-Test für BRIDGE-0038), kein echter Fehler.
- **Damit sind alle Aufträge BRIDGE-0017 bis BRIDGE-0038 `ARCHIVED`.**
  Höchste vergebene ID: **BRIDGE-0038**. Nächste freie ID: **BRIDGE-0039**.
  Kein Auftrag `RUNNING`, kein `git status`-Rest, nichts Ungepushtes.

### Zwei Dokumentationsfehler entdeckt (noch nicht korrigiert — siehe Abschnitt 3)

- **`docs/ACB-PROJEKT-INTEGRATION.md`** behauptet weiterhin, die
  `task_prefix`-Kollisionsprüfung zwischen Projektprofilen sei „aktuell
  nicht verdrahtet". Das stimmt seit **BRIDGE-034** nicht mehr — frisch
  gegen den echten Code geprüft: `src/bridge/store.py` hat
  `_check_task_prefix_collision()`, aktiv aufgerufen in `create_task()`.
  Das Dokument ist an dieser Stelle veraltet.
- **`docs/ACB-ORCHESTRATOR-KONZEPT.md`** führt in seiner Roadmap-Tabelle
  **BRIDGE-0031** als „Eigentliche Orchestrator-Auslöselogik (geplant)".
  Der real archivierte BRIDGE-0031 hat aber einen **anderen** Inhalt:
  „Maschinenauflösung vereinheitlichen" (`registry.machine_name()` an
  allen Schreibstellen verdrahten, BUGFIX, aus Übergabe v9 Kontext).
  **Die eigentliche Orchestrator-Auslöselogik ist unter keiner erkennbaren
  ID umgesetzt worden** — nicht angenommen, sondern hier offen benannt.
  Falls sie weiterhin gewünscht ist, braucht sie eine neue BRIDGE-ID und
  eine korrigierte Roadmap-Tabelle.

---

## 1. Offene Aufträge — Reihenfolge

**Keine.** Aktuell ist kein Arbeitspaket spezifiziert und kein Auftrag im
Store angelegt. Nächste freie ID: **BRIDGE-0039**.

---

## 2. Wichtige technische Entscheidungen dieser Sitzung

Keine — reine Verifikationssitzung, keine neuen fachlichen oder
technischen Entscheidungen getroffen.

---

## 3. Noch zu tun, bewusst benannt statt vergessen

Aus v10 unverändert offen (nicht erneut geprüft in dieser Sitzung, außer
wo vermerkt):

- **Doku-Korrektur „Ein-Auftrag-zur-Zeit" pro Projekt statt global** in
  `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` — reine Textänderung, weiterhin
  nicht gemacht.
- **`board`-Klon** (dritter, neutraler Checkout nur für den Web-UI-
  Server) — weiterhin **nicht** angelegt. Server läuft weiterhin aus
  `claude` heraus.
- **Codex-WSL-Setup real durchführen** — `ACB_PROJECT_BASE` muss dort
  tatsächlich gesetzt werden, weiterhin nur besprochen, nie ausgeführt.
- **Realer Zwei-Schreiber-Test** (Codex + Claude Code gleichzeitig, echte
  Pushes gegen denselben Remote) — weiterhin nie unter echter Last
  geprüft.
- **Reste des alten `E:\_DEV\Codex-Control-Bridge`-Ordners** auf HAM11
  und DES11 — weiterhin funktional bedeutungslos, Aufräumen bei
  Gelegenheit.
- **WSL-Worktree-Pfad für den Dorfschaft-Piloten** weiterhin nicht
  bestätigt (`/mnt/e/_DEV/Dorfschaft-worktrees/AP15-RP2-HAM01`, laut
  ChatGPT „voraussichtlich", nie verifiziert).

Neu in dieser Sitzung entdeckt:

- **`docs/ACB-PROJEKT-INTEGRATION.md` korrigieren** — Abschnitt zur
  `task_prefix`-Kollisionsprüfung ist seit BRIDGE-034 falsch (siehe
  Abschnitt 0), muss auf „automatisch erzwungen, `_check_task_prefix_
  collision()` in `store.py`" umgestellt werden, inkl. der
  zusammenfassenden Tabelle am Dokumentende.
- **`docs/ACB-ORCHESTRATOR-KONZEPT.md` Roadmap-Tabelle korrigieren** —
  BRIDGE-0031-Zeile beschreibt nicht mehr, was der Auftrag tatsächlich
  war. Zusätzlich fachlich klären: wird die ursprünglich für BRIDGE-0031
  vorgesehene Orchestrator-Auslöselogik noch gebraucht? Falls ja, neue
  BRIDGE-ID vergeben.

---

## 4. Nicht von selbst anfangen bei

- Kein echter `DORF-*`-Pilotauftrag — BRIDGE-0035 ist jetzt zwar durch,
  aber der WSL-Pfad ist **weiterhin nicht bestätigt** (siehe Abschnitt 3),
  beide Bedingungen aus v10 müssen weiterhin gemeinsam erfüllt sein.
- Keine allgemeine `read_only`-Durchsetzung für alle `task_class`-Werte
  bauen (eigenes, bewusst zurückgestelltes Thema).
- Kein Linux-Executor-Dienst, kein API-/MCP-Steueradapter für ChatGPT,
  kein Auftrags-Locking, keine Actor-Identitätsverifikation — weiterhin
  bewusst als „für den Piloten nicht nötig" eingeordnet.
- `task_prefix: BRIDGE` nicht erneut zur Debatte stellen, außer der
  Nutzer bringt es selbst wieder auf.
- Keine Orchestrator-Auslöselogik selbstständig unter einer neuen ID
  anfangen, ohne das vorher mit April zu klären (siehe Abschnitt 3) —
  könnte inzwischen fachlich obsolet oder anders priorisiert sein.
