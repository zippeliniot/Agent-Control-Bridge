# ACB — Neues Projekt einbinden: Schritt für Schritt (v1)

Ausgangslage: Das GitHub-Repo des Projekts existiert und du hast die URL.
Voraussetzung: `ACB-INTEGRATION-GENERISCH-v1.md`, `ACB-STEUERCHAT-START-GENERISCH-v2.md` und `ACB-DOKUMENTENUEBERSICHT-v1.md` liegen in `docs/` des ACB-Repos (gepusht).
Du tippst nur die Repo-URL. Alles andere liefert der ACB-Steuerchat mit konkreten Werten.

| # | WO | Was | Ergebnis |
|---|---|---|---|
| 1 | Zielrepo, GitHub im Browser | Prüfen: Branch `main` mit mindestens einem Commit (ein leeres Repo hat keinen HEAD, dann eine README anlegen). Ist es privat, vorher klären, ob der Steuerchat es ohne Login klonen kann. | Repo klonbar, `main` vorhanden |
| 2 | ACB-Steuerchat (dieser Chat) | Nachricht: die Repo-URL, dazu ob `claude-code` (Standard) oder `codex` ausführt. Der Chat klont das Repo, liest die README, schlägt `project_id` und Präfix vor, prüft gegen `project list` auf Kollision und wartet auf dein OK. | `project_id`, Präfix, Executor bestätigt |
| 3 | Download | Der Chat liefert `projects/<id>/project.yaml` und einen PowerShell-Block mit konkreten Werten. | Profil-Datei und Block liegen vor |
| 4 | PowerShell (aktive Maschine) | Block ausführen. Er legt an: das Profil im ACB-Repo (commit, push), den Zielrepo-Klon unter `E:\_DEV\<Repo>`, den ACB-Klon `E:\_DEV\Agent-Control-Bridge\projects\<Repo>` mit `.venv` und Requirements, und führt `project validate` aus. | Validate ohne Fehler, Profil auf GitHub |
| 5 | ACB-Steuerchat | Zielrepo-`CLAUDE.md` (Executor-Regeln) entwerfen lassen. Kommt als Download. | Entwurf liegt vor |
| 6 | PowerShell | Im Zielrepo ablegen, committen, pushen (Block vom Chat). | `CLAUDE.md` auf GitHub |
| 7 | claude.ai, Browser | Neues Projekt anlegen. Als Custom Instructions den Text aus `ACB-STEUERCHAT-START-GENERISCH-v2.md` (ab der Linie) einfügen. Einziges Feld: `{{PROJEKT_ID}}` durch die bestätigte `project_id` ersetzen. | Projekt-Steuerchat bereit |
| 8 | Neuer Projekt-Chat | Eine beliebige erste Nachricht senden (z. B. „Start"). Der Chat klont beide Repos, leitet alle Werte aus dem Profil ab und antwortet in höchstens 10 Zeilen. | Erste Antwort |
| 9 | Neuer Projekt-Chat | Erste Antwort gegenlesen: Name, Präfix, Zielrepo, Executor, lokaler Pfad, beide HEADs. Stimmt etwas nicht, Profil korrigieren (Schritt 2–4 wiederholen), nicht im Chat weitermachen. | Werte bestätigt |
| 10 | Neuer Projekt-Chat | Ersten Auftrag beschreiben. Ab hier gilt der Auftragsablauf aus `ACB-INTEGRATION-GENERISCH-v1.md`, Abschnitt 3. | Erstes Work-Package |

## Wenn etwas hakt

- **`project validate` schlägt fehl:** Profil nicht ändern, Fehlertext dem ACB-Steuerchat geben.
- **Chat meldet „Profil nicht gefunden":** `project_id` im Startprompt weicht vom Verzeichnisnamen unter `projects/` ab (Tippfehler). Der Chat nennt die vorhandenen IDs.
- **Chat kann das Zielrepo nicht klonen:** Repo ist privat. Mit April klären, bevor ein Auftrag zugeschnitten wird.
- **Zweite Maschine:** Schritt 4 (Klone und `.venv`) dort einmal wiederholen, bevor dort am Projekt gearbeitet wird. `registry.yaml` muss die Maschine kennen.
