# Maschinen-, Umgebungs- und Ausführungsregister

> **Status:** verbindlich ab BRIDGE-001.
> Grundlage: Konzept-Abschnitt 9 (Maschinenmodell). Maschinenidentität wird
> **nicht allein aus einem Hostnamen** abgeleitet.

## Register

**Korrigiert 19.09.2026 (Topologie-Entscheidung April, DES11 umgesetzt,
HAM11 folgt bei nächster Rotation):** vier getrennte lokale Klone pro
Maschine statt zwei. `claude\` ist seitdem **kein** ACB-Entwicklungs-
Checkout mehr — siehe Ausführungsmodell unten.

| Klon | Zweck | Betrieb durch |
|------|-------|----------------|
| `E:\_DEV\Agent-Control-Bridge\board` | Einzige Web-UI-/Writer-Instanz für den ACB-Store (`bridge webui serve`) | Steuerchat/April |
| `E:\_DEV\Agent-Control-Bridge\dev` | ACB-Quellcode-Entwicklung (BRIDGE-Aufträge, die die Bridge selbst ändern) | Claude Code |
| `E:\_DEV\Agent-Control-Bridge\claude` | Ausschließlich Produkt-/Projektarbeit mit Claude Code, **keine** ACB-Entwicklung | Claude Code |
| `E:\_DEV\Agent-Control-Bridge\codex` | Codex-Checkout (Windows-nativ oder WSL, je nach Auftrag) | Codex |

| Physische Maschine | Logische Umgebung | OS | Stand |
|--------------------|-------------------|----|-------|
| `HAM11` | `HAM01` | Windows (+ Ubuntu/WSL für Codex) | **alte Topologie (`claude`/`codex`), Umstellung ausstehend, nächste Rotation** |
| `DES11` | `DES01` | Windows (+ Ubuntu/WSL für Codex) | **neue Topologie (`board`/`dev`/`claude`/`codex`), umgesetzt 19.09.2026** |

Bis zur Umstellung auf HAM11: dort gilt weiterhin die alte Zuordnung
(`claude\` = ACB-Entwicklung **und** Web-UI, `codex\` unverändert) — bei
jeder Aussage über „den Klon" explizit prüfen, welche Maschine gemeint ist.

Codex nutzt unter WSL die Umgebungsvariable `ACB_PROJECT_BASE`, die auf den
eigenen `codex`-Klon zeigt — keine Änderung an `registry.yaml` nötig, die
Registry bleibt für die Befehlsreferenz (`bridge commands`) zuständig.

Beide Systeme sind **physisch getrennte Maschinen**. Das Laufwerk `E:` ist auf
HAM11 und DES11 nur **namensgleich**, nicht geteilt — es gibt keine gemeinsame
Platte. Die beiden lokalen Arbeitskopien sind unabhängig und treffen sich
**ausschließlich über GitHub**.

## Ausführungsmodell (verbindlich)

Rollen:

- **Claude Code — native Windows-App** = ausführende Instanz. Arbeitet in
  `E:\_DEV\Agent-Control-Bridge\dev` (auf DES11), wenn der Auftrag die Bridge
  selbst ändert (`task_class: BUGFIX`/`FEATURE` am Bridge-Quellcode), sonst in
  `E:\_DEV\Agent-Control-Bridge\claude` (reine Produkt-/Projektarbeit, kein
  ACB-Quellcode). Ändert Dateien, führt Tests aus, committet und pusht. Läuft
  **nicht** in der Ubuntu/WSL-Umgebung.
- **Web-UI/Writer** = einzige schreibende Instanz für den ACB-Store, läuft
  ausschließlich aus `E:\_DEV\Agent-Control-Bridge\board` (auf DES11) heraus
  (`bridge webui serve`). Kein anderer Klon startet die Web-UI.
- **Claude im Browser** = Steuer- und Review-Ebene (Architektur, Zuschnitt der
  Arbeitspakete, Prüfung des gepushten Stands). Fasst das Repo nicht direkt an.
- **GitHub** = einziger Austauschkanal zwischen HAM11 und DES11 und SSOT.

Begründung der Isolationsstrategie: Da das Repo auf der Windows-Seite (`E:`)
liegt, wird Claude Code nativ unter Windows betrieben. Dadurch ist es
**strukturell** von der Ubuntu/WSL-Umgebung getrennt, die Codex für Dorfschaft
nutzt — es ist nicht in dieser Linux-Instanz und kann sie nicht verändern. Der
native-Windows-Betrieb hat keine bubblewrap-Sandbox (die ist WSL2/Linux/macOS-
only); die Kompensation erfolgt über die Guardrails in `CLAUDE.md` und
`.claude/settings.json` (u. a. Sperre von `\\wsl.localhost\`), Git for Windows
für ein zuverlässiges Bash-Tool sowie die Begrenzung auf das Repo-Verzeichnis.

## Schutzbereich (verbindlich)

- **Ubuntu/WSL nicht verändern** und **Dorfschaft nicht anfassen** (Ausnahme nur
  ausdrückliche Read-only-Aufträge BRIDGE-011/012).
- Claude Code greift **nicht** über `\\wsl.localhost\...` oder `wsl`-Aufrufe in
  die Linux-Distros hinein.
- Claude Code arbeitet ausschließlich innerhalb des jeweils zugewiesenen
  Klons (`dev\` für ACB-Entwicklung, `claude\` für Produktarbeit — nie
  vermischt).
- Erfordert eine Aufgabe eine System- oder WSL-Änderung → **fail-closed**:
  anhalten, `BLOCKED`, Rückfrage an den Steuerprozess.

## Wöchentlicher Wechsel (Rotation)

GitHub ist der **einzige** Übergabekanal. Vor jedem Wechsel muss **alles** auf
GitHub liegen — Code **und** fachliche Dokumente.

| Tag | Aktion | Quelle → Ziel |
|-----|--------|---------------|
| **Donnerstag** | 100 % Upload auf GitHub | `HAM11`/`HAM01` → GitHub |
| **Freitag** | Weiterbearbeitung | GitHub → `DES11`/`DES01` |
| **Montag** | Rückgabe (vorher 100 % Upload) | `DES11`/`DES01` → GitHub → `HAM11`/`HAM01` |

Regel: **Kein Wechsel ohne vollständigen, gepushten Stand.** Prüfung über
`scripts/handover-check.ps1` (Windows/PowerShell) bzw. `scripts/handover-check.sh`
(Git Bash) — fail-closed bei nicht gepushten Änderungen, unsauberem Working Tree,
Stashes oder fehlenden Pflichtdokumenten.
