# BRIDGE-034 — Dorfschaft/Codex-Integrationsgrundlage härten (Profil, CODEX.md, task_prefix-Kollision)

| Feld | Wert |
|------|------|
| bridge_task_id | BRIDGE-0034 |
| project_id | codex-control-bridge |
| task_class | BUGFIX |
| depends_on | (keine) |
| permission | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| executor | claude-code |
| review_roles | lead: anthropic, support: openai (aus Projektprofil übernommen — bei diesem Auftrag besonders wichtig, da er die Dorfschaft/Codex-Integration betrifft) |
| Modell/Denkstufe | Claude Sonnet 5, Denkstufe MEDIUM — zwei Punkte sind mechanisch (Profil-Flag, Doku-Korrektur), der dritte (`task_prefix`-Kollisionsprüfung) ist eine neue, aber klar umrissene Geschäftsregel nach demselben Muster wie BRIDGE-032 — kein neuer Zustand, keine Architekturentscheidung, daher nicht HIGH. |

> **Verbindlich für diesen und jeden CCB-Auftrag:**
> - Jede Zustandsänderung läuft über die Bridge-CLI, kein direktes Bearbeiten
>   von Store-Dateien.
> - `GIT_PUSH` steht im Profil — nach `run finish` **muss** gepusht werden,
>   idealerweise über `--commit`, und **sofort**, nicht gesammelt.
> - **Nichts in diesem Auftrag berührt das echte Dorfschaft-Repository** —
>   nur CCB-eigene Dateien (`projects/dorfschaft/project.yaml`, `CODEX.md`,
>   `src/bridge/store.py`). Kein Zugriff auf `zippeliniot/dorfschaft`.

## Kontext

Ausgelöst durch eine Bereitschaftsprüfung von ChatGPT (OpenAI-Seite,
Controller-Rolle für Codex/Dorfschaft), gegengeprüft vom Steuerchat gegen
den frischen Code. Ziel: die CCB-seitige Integrationsgrundlage für den
späteren ersten echten Dorfschaft/Codex-Testauftrag (`DORF-xxx`,
`task_class: READONLY_CHECK`) sauber machen — **ohne** diesen Testauftrag
selbst schon anzulegen.

**Drei konkrete, verifizierte Befunde:**

1. **`projects/dorfschaft/project.yaml` hat `read_only: false`**,
   `git_policy.allow_push: true`. Per `git log --follow` bestätigt: keine
   Altlast, sondern eine bewusste Entscheidung aus Commit `69a5d9b`
   („dorfschaft jetzt schreibend (Codex/ChatGPT)"), die aber nie in
   `README.md`/`docs/CCB-PROJEKT-INTEGRATION.md` nachgezogen wurde — beide
   sagen weiterhin explizit „Die erste reale Integration ist ein reiner
   Read-only-Test." Für den bevorstehenden ersten Pilotlauf wird das Profil
   **vorübergehend** auf `read_only: true` zurückgesetzt (Nutzer-
   Entscheidung nach dem ChatGPT-Audit, kein automatisches „Zurückrudern").
   **Wichtige Einschränkung, im Code verifiziert:** `read_only: true`
   greift technisch **nur** für den separaten Beobachtungs-Adapter
   (`src/bridge/adapter.py`, `ReadOnlyProjectAdapter` — lehnt bei
   `profile.get("read_only") is not True` hart ab). Es gibt **keine**
   allgemeine Durchsetzung von `read_only` gegen normale
   `task_class: FEATURE`-Aufträge mit Schreibrechten — `profiles.py`
   kommentiert das selbst als bewusst offen. Die technische Absicherung
   des ersten Pilotlaufs kommt aus **BRIDGE-032** (`READONLY_CHECK` ⇒
   zwingend `permissions: [READ_ONLY]`, fail-closed) auf Auftragsebene,
   nicht aus diesem Profil-Flag allein — dieser Auftrag korrigiert das
   Flag trotzdem, weil es die dokumentierte Absicht wiederherstellt und
   den Adapter-Mechanismus für Dorfschaft nutzbar macht, **nicht** weil er
   allein schon ausreichend schützt.
2. **`CODEX.md` behauptet weiterhin „kein aktives Projektprofil mit
   executor: codex"** — tatsächlich bestehen bereits drei
   (`bess-msrechner`, `bess-platform`, `dorfschaft`), keins davon je
   praktisch genutzt (`grep -c '"actor": "codex' audit/audit.jsonl` = 0).
   Die Kernaussage (nie praktisch erprobt) bleibt richtig, nur die
   Formulierung ist falsch.
3. **`task_prefix`-Kollision wird nicht technisch verhindert.**
   `src/bridge/profiles.py`, Modul-Docstring, wörtlich: „die Verdrahtung
   in Store/Runner (task_prefix erzwingen, ...) folgt bewusst später
   (BRIDGE-011)" — BRIDGE-011 lieferte aber nur den Adapter-Mechanismus
   (Befund 1), nicht diese Prüfung. Aktuell sind alle sieben Präfixe
   zufällig eindeutig (`BESSMS`, `BESSPLT`, `CLIMAC`, `BRIDGE`, `DORF`,
   `TANKEN`, `WETTER`), aber nichts verhindert, dass ein künftiges Profil
   einen bestehenden Präfix wiederverwendet und `bridge_task_id`-Räume
   stillschweigend vermischt.

**Ausdrücklich NICHT Teil dieses Auftrags** (bewusst abgegrenzt, nicht
vergessen):
- **WSL-/Worktree-Pfadauflösung** für den konkreten Dorfschaft-
  AP15-RP2-Checkout. Der reale Linux-Mountpfad ist vom Steuerchat aus
  nicht verifizierbar, ohne zu raten — widerspräche „keine Erfindungen".
  Folgt als eigener Auftrag (voraussichtlich BRIDGE-0035), sobald der
  tatsächliche Pfad von Mensch/Codex bestätigt ist. Hinweis für später:
  `registry.py`/`resolve_base()` hat bereits eine Override-Env-Var
  (`CCB_PROJECT_BASE`) — evtl. ausreichend für die WSL-Seite, ohne neues
  Schema-Feld, aber das ist eine Vermutung, kein Ergebnis dieses Auftrags.
- **Allgemeine `read_only`-Durchsetzung** für alle `task_class`-Werte
  (nicht nur den Adapter). Größeres, eigenständiges Architekturthema,
  nicht Teil dieser Härtung.
- **`AGENTS.md` im Dorfschaft-Repo selbst** — liegt außerhalb des
  CCB-Repos, wäre eine Änderung am fremden Repository, nicht Teil dieses
  Auftrags.

## Von Claude Code umzusetzen

1. Auftrag anlegen und starten:
   ```
   bridge task create tasks/incoming/BRIDGE-0034.yaml
   bridge run start BRIDGE-0034 --actor claude-code
   ```

2. **`projects/dorfschaft/project.yaml`:**
   - `read_only: false` → `read_only: true`.
   - `git_policy.allow_push: true` → `false` (konsistent zum
     Read-only-Zustand — ein Push-Recht bei `read_only: true` wäre
     widersprüchlich, selbst wenn es aktuell nirgends geprüft wird).
   - Kommentar am Dateianfang ergänzen: kurz, dass dies der bewusste
     Rücksprung auf den ursprünglich vorgesehenen Read-only-Pilotzustand
     ist (mit Verweis auf BRIDGE-034 und den vorherigen Commit
     `69a5d9b`), nicht eine Ablehnung der späteren Schreibintegration —
     spätere Sitzungen sollen den Kontext haben, nicht raten müssen.

3. **`CODEX.md`:** den Status-Absatz korrigieren — drei aktive Profile
   mit `executor: codex` (`bess-msrechner`, `bess-platform`,
   `dorfschaft`), keins bisher praktisch genutzt (Audit-Trail-Beleg wie
   oben). Rest des Dokuments (WSL-Zugriffspfad „nicht dokumentiert
   bestätigt") unverändert lassen — das stimmt weiterhin.

4. **Neue fail-closed Geschäftsregel in `src/bridge/store.py`,
   `create_task()`:** Vor dem Schreiben prüfen, ob `task_prefix` des
   Zielprojekts (aus `projects/<project_id>/project.yaml`, über
   `profiles`-Modul laden) mit dem `task_prefix` eines **anderen**
   bereits vorhandenen Projektprofils kollidiert. Kollidiert er → fail-
   closed `StoreError` mit Klartext (welche zwei `project_id`s
   betroffen, welcher Präfix). Platzierung: eigene kleine Methode
   analog `_check_readonly_consistency()` aus BRIDGE-032, aus
   `create_task()` aufgerufen — **nicht** in `save_task()`, da
   `task_prefix` eine Projekteigenschaft ist, keine Auftragseigenschaft
   (ein bestehender Auftrag ändert seinen `task_prefix` nie nachträglich).
   Die Prüfung muss **alle** Projektprofile unter `projects/*/` einlesen,
   nicht nur das Zielprofil — Wiederverwendung der bestehenden
   `profiles`-Ladefunktionen, kein Duplicated Code.

5. **Tests** (`tests/test_store.py`, bestehendes Muster wiederverwenden):
   - Zwei Projektprofile mit identischem `task_prefix` (temporär im
     Test-Tmp-Verzeichnis angelegt) → `create_task()` für das zweite
     wirft `StoreError`.
   - Bestehende sieben echte Profile bleiben beim Anlegen eines
     normalen Auftrags weiterhin kollisionsfrei (Regressionscheck gegen
     die echten `projects/*/project.yaml`-Dateien, nicht nur synthetisch).
   - `tests/test_profiles.py` (falls vorhanden) oder `test_store.py`:
     ein Test, der bestätigt, dass `projects/dorfschaft/project.yaml`
     jetzt `read_only: true` hat (einfacher Regressionsanker gegen
     versehentliches erneutes Zurückflippen ohne bewusste Entscheidung).
   - Volle Testsuite frisch laufen lassen, dreimal, tatsächlich
     nachzählen (Referenzwert vor diesem Auftrag: 359 Tests).

6. Pflicht-Footer + Abschluss, `--commit` nutzen, **sofort pushen**:
   ```
   bridge run finish BRIDGE-0034 --status COMPLETED --actor claude-code \
     --commit \
     --summary "Dorfschaft/Codex-Integrationsgrundlage gehaertet: projects/dorfschaft/project.yaml read_only auf true zurueckgesetzt (git_policy.allow_push auf false, Kommentar mit Begruendung/Verweis auf BRIDGE-034 und Commit 69a5d9b ergaenzt) - bewusster Ruecksprung auf den urspruenglich vorgesehenen Read-only-Pilotzustand, keine dauerhafte Ablehnung der spaeteren Schreibintegration. CODEX.md-Statusabsatz korrigiert (drei aktive codex-Profile statt 'keins', weiterhin nie praktisch genutzt). Neue fail-closed task_prefix-Kollisionspruefung in store.py create_task() - bisher technisch nicht erzwungen (profiles.py-Kommentar bestaetigte das). WSL-Pfadaufloesung und allgemeine read_only-Durchsetzung fuer alle task_class-Werte bewusst nicht Teil dieses Auftrags, siehe Kontext-Abschnitt im Work-Package."
   git push
   ```
   `Auftrag: BRIDGE-0034 / Lauf: RUN-01 / Status: COMPLETED`

## Akzeptanzkriterien

- [x] `projects/dorfschaft/project.yaml`: `read_only: true`,
      `git_policy.allow_push: false`, erklärender Kommentar mit Verweis
      auf BRIDGE-034 und Commit `69a5d9b`.
- [x] `CODEX.md`: Statusabsatz korrigiert (drei aktive Profile, weiterhin
      nie praktisch genutzt), Rest unverändert.
- [x] `create_task()` lehnt einen neuen Auftrag fail-closed ab, wenn
      dessen Zielprojekt einen `task_prefix` trägt, der mit einem
      anderen bestehenden Projektprofil kollidiert.
- [x] Kollisionsprüfung liest alle Profile unter `projects/*/`, nicht
      nur das Zielprofil.
- [x] `save_task()` bleibt unverändert (Kollisionsprüfung nur bei
      `create_task()`).
- [x] Neue Tests: synthetische Kollision wird abgelehnt; die sieben
      echten bestehenden Profile bleiben beim normalen Auftraglegen
      unverändert funktionsfähig (kein falsches Positiv).
- [x] Regressionsanker-Test: `dorfschaft`-Profil hat `read_only: true`.
- [x] Kein Zugriff auf das echte Dorfschaft-Repository in diesem Auftrag
      (ausschließlich `projects/dorfschaft/project.yaml`, `CODEX.md`,
      `src/bridge/store.py`, `tests/test_store.py` geändert).
- [x] Volle Testsuite (bestehend + neu) dreimal frisch grün, frischer
      Klon verifiziert (363 Tests je Lauf: 359 Basis + 4 neu; drei
      separate `unittest discover`-Läufe grün gezählt).
- [x] Jeder Commit sofort gepusht, nicht gesammelt.
