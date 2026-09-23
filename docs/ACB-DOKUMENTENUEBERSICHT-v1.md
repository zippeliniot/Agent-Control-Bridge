# ACB — Dokumentenübersicht für neue Projekte (v1)

Stand: 2026-09-23. Zielort im Repo: `docs/ACB-DOKUMENTENUEBERSICHT-v1.md`.
Beantwortet vier Fragen: welches Dokument wofür und wann, wo Eingaben passieren, was vorab auf GitHub stehen muss, in welcher Reihenfolge.

## 1. Welches Dokument, wofür, wann

| Dokument | Ort | Wofür | Wann / durch wen |
|---|---|---|---|
| `ACB-STEUERCHAT-START-GENERISCH-v2.md` | ACB-Repo `docs/`; Text wird in claude.ai eingefügt | Startprompt eines Projekt-Steuerchats. Enthält Startablauf, Kommunikationsregeln, Prüfregeln. | **Einmal je Projekt**, von April in die Custom Instructions des neuen claude.ai-Projekts eingefügt. Fertig befüllt per `scripts\steuerchat-vorlage.py --project-id <id>` (prüft die ID gegen die Profile, kein manuelles Ersetzen). |
| `ACB-INTEGRATION-GENERISCH-v1.md` | ACB-Repo `docs/` | Referenz: Einrichtung, Auftragsablauf, Vorlagen (Profil, Staging-YAML, Work-Package, Claude-Code-Anweisung), Prüfung, CLI. | Der Steuerchat liest sie beim Start selbst. April nutzt sie für die einmalige Einrichtung (Abschnitt 2 dort). |
| `projects/<id>/project.yaml` | ACB-Repo | Projektprofil: einzige Quelle für Name, Präfix, Zielrepo, Executor, Rechte. | **Einmal je Projekt**, vor dem ersten Chat. Steuerchat liefert die Datei, April committet. |
| `CLAUDE.md` im Zielrepo | Zielrepo | Regeln für den Executor im Produktcode (Scope, Tests, Fail-closed). | Einmal je Projekt, empfohlen vor dem ersten Auftrag. |
| `work-packages/<PRAEFIX>-<NNN>.md` | ACB-Repo | Ein Auftrag: Ablauf, Teile, Haken. Vom Steuerchat als Download geliefert. | **Je Auftrag**. April legt ab und committet. |
| `tasks/incoming/<ID>.yaml` | ACB-Klon lokal, gitignored | Staging-YAML zum Anlegen des Auftrags im Store. | Je Auftrag. April legt lokal ab, nicht committen. |
| `docs/handover/<Präfix>-STEUERCHAT-UEBERGABE-v<N>.md` | ACB-Repo | Stand am Sitzungsende: Änderungen, HEADs, offene Entscheidungen, „nicht von selbst anfangen bei". | **Am Ende jeder Sitzung** oder vor Chatwechsel. Steuerchat liefert, April committet. Nächster Chat liest die höchste Version. |

**Ältere Dokumente und ihr Geltungsbereich:**
- `ACB-STEUERCHAT-STANDARDSTART.md` = nur ACB-Kern-Steuerchat.
- `ACB-PROJEKT-INTEGRATION.md` = Detailreferenz zu Profilfeldern, Ablauf steht in der Integrationsdatei.
- `ACB-STEUERCHAT-VORLAGE.md` = entfernt (BRIDGE-0072).
- `scripts/steuerchat-vorlage.py` = füllt jetzt den Startprompt v2.

## 2. Wo welche Eingabe gemacht wird

| Eingabe | Wo | Wie oft |
|---|---|---|
| `project_id` | Startprompt in den claude.ai-Custom-Instructions (`{{PROJEKT_ID}}`) und im Profil (`project_id`) | einmal je Projekt, beide Stellen müssen übereinstimmen |
| Projektname, Präfix, Zielrepo, Executor, Repo-Verzeichnis | nur im Profil `projects/<id>/project.yaml` (`description`, `task_prefix`, `github_repo`, `executor`, `repository`) | einmal je Projekt |
| Maschinen und Basispfad | `registry.yaml` (nur ändern, wenn eine neue Maschine dazukommt) | selten |
| Auftragsinhalt | Steuerchat schreibt Work-Package und Staging-YAML, April tippt nichts | je Auftrag |
| `EXPECTED_HEAD` | Claude Code ersetzt den Platzhalter in der Staging-YAML selbst | je Auftrag |
| Ablage der Dateien | PowerShell-Block, den der Steuerchat mit konkreten Werten liefert | je Auftrag |
| Auftrag an Claude Code | eine Nachricht, vom Steuerchat kopierfertig geliefert, im ACB-Klon geöffnetes Claude Code | je Auftrag |
| Kopiert → Review, Archivieren | Web-UI (`board`-Klon) oder CLI, durch April | je Auftrag |

Der Steuerchat leitet alles aus dem Profil ab und zeigt die abgeleiteten Werte in seiner ersten Antwort in einer Zeile zur Sichtprüfung an.

## 3. Was vorab auf GitHub stehen muss

Vor dem ersten Start des Steuerchats, alles auf `main` und gepusht:

**ACB-Repo `zippeliniot/Agent-Control-Bridge`**
- [ ] `docs/ACB-INTEGRATION-GENERISCH-v1.md` und `docs/ACB-STEUERCHAT-START-GENERISCH-v2.md` sind eingecheckt.
- [ ] `projects/<id>/project.yaml` ist eingecheckt und mit `project validate` geprüft. `project_id` gleich Verzeichnisname, `task_prefix` eindeutig (1–8 Großbuchstaben), `github_repo` als `org/repo`, `executor` gesetzt.
- [ ] `registry.yaml` enthält jede Maschine, auf der am Projekt gearbeitet wird (aktuell HAM11 und DES11).

**Zielrepo (Produkt)**
- [ ] Das Repo existiert auf GitHub, Branch `main`, mindestens ein Commit.
- [ ] Der Steuerchat kann es ohne GitHub-Login klonen (er hat keine Zugangsdaten). Ist es privat, scheitert Startschritt 5. Das vorher mit April klären.
- [ ] Ein `CLAUDE.md` mit den Executor-Regeln ist eingecheckt (empfohlen).

**Lokal, nicht GitHub (Voraussetzung für Claude Code)**
- [ ] Zielrepo ausgecheckt unter `<Basis>\<repository>`, Working Tree sauber.
- [ ] ACB-Klon `E:\_DEV\Agent-Control-Bridge\projects\<repository>` mit `.venv` und installierten Requirements.

Der Steuerchat liest die Repos frisch von GitHub. Was nicht gepusht ist, sieht er nicht und kann es nicht prüfen.

## 4. Reihenfolge

1. Präfix und `project_id` festlegen, Profil erstellen, validieren, pushen.
2. Zielrepo und `CLAUDE.md` bereitstellen und pushen.
3. Lokale Klons anlegen.
4. claude.ai-Projekt anlegen, Startprompt mit `project_id` einfügen, Chat starten.
5. Erste Antwort des Steuerchats gegenlesen (abgeleitete Werte, HEADs).
6. Auftragsschleife wie in `ACB-INTEGRATION-GENERISCH-v1.md` Abschnitt 3 und 4.
7. Sitzungsende: Übergabedatei ablegen.
