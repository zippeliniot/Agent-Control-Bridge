# Push-Sperre in `claude` und `codex` - Nachweis (BRIDGE-0057)

Zweck: Die Klone `claude` und `codex` (Produktarbeit) koennen nichts nach GitHub
pushen. Zwei unabhaengige Schichten; jede fuer sich genuegt, beide zusammen
sind Pflicht. `dev` und `board` sperren wir **nicht** (Writer, behalten Push).

Pfade unten relativ zu `E:\_DEV\Agent-Control-Bridge\`. Ausfuehrung durch April,
je Klon einmal, in PowerShell.

## Schicht 1 - Tool-Deny (Agent darf `git push` nicht aufrufen)

**Klon `claude` (Claude Code):** Datei `claude\.claude\settings.local.json`
anlegen bzw. ergaenzen (**nicht committen**; die Datei ist lokal):

```json
{
  "permissions": {
    "deny": ["Bash(git push:*)", "PowerShell(git push:*)"]
  }
}
```

**Klon `codex` (Codex):** Regel in `%USERPROFILE%\.codex\rules\default.rules`
(Prefix-Rule, gilt fuer die Codex-Instanz auf dieser Maschine):

```
prefix_rule(pattern=["git", "push"], decision="forbidden")
```

> Hinweis: Die Codex-Regel-Syntax gegen die installierte Codex-Version pruefen
> (`codex execpolicy check --rules <Datei> git push`). Schicht 2 bleibt davon
> unabhaengig und ist die harte Sperre.

## Schicht 2 - Git (Push-URL ist ungueltig)

In **jedem** der beiden Klone:

```powershell
git remote set-url --push origin DISABLED
git remote -v
```

Erwartet: `origin ... (fetch)` zeigt die echte URL, `origin ... (push)` zeigt
`DISABLED`. Fetch/Pull bleiben moeglich.

## Nachweis je Klon

In jedem Klon ausfuehren:

```powershell
git push --dry-run
```

Muss **scheitern** (Exit-Code ungleich 0, z. B. `fatal: 'DISABLED' does not
appear to be a git repository`). Ausgabe unten einfuegen.

| Klon | Datum | Schicht 1 gesetzt | Schicht 2 gesetzt | Ausgabe `git push --dry-run` | Exit-Code | Ergebnis |
|---|---|---|---|---|---|---|
| `claude` | 2026-09-20 | [x] | [x] | fatal: not a git repository (Push-URL DISABLED) | 128 | PASS |
| `codex` | 2026-09-20 | n/a (global) | [x] | fatal: not a git repository (Push-URL DISABLED) | 128 | PASS |

## Gegenprobe (Writer bleiben Writer)

In `dev` und `board` darf `git push --dry-run` **nicht** an einer Sperre
scheitern (`Everything up-to-date` oder Dry-Run-Ausgabe). Dort weder
Schicht 1 noch Schicht 2 setzen.

| Klon | Datum | Ausgabe `git push --dry-run` | Ergebnis |
|---|---|---|---|
| `dev` | 2026-09-20 | Everything up-to-date | PASS |
| `board` | 2026-09-20 | Everything up-to-date | PASS |

## Transfer - Draft vom Executor zum Board (BRIDGE-0057 Teil B)

**Regel:** Der Executor (`claude`/`codex`) committet den Draft lokal
(`bridge draft write --commit`), pusht aber **nie**. Das Board holt den
Commit per lokalem Pfad aus dem Executor-Klon (`git pull <Pfad> main`),
importiert ihn (`bridge draft import`) und ist die **einzige** Stelle, die
nach GitHub pusht.

Pfade DES11, Basis `E:\_DEV\Agent-Control-Bridge\`. `BR` =
`.venv\Scripts\python.exe src\bridge\cli.py --root . --schema-dir schemas`.
Nur Windows-native Klone; ein Codex-Klon unter WSL wird nicht per
`\\wsl...`-Pfad gezogen (CLAUDE.md Regel 2) - dort Transfer durch April.

**1. Klon `claude` (Executor, kein Push):**

```powershell
cd E:\_DEV\Agent-Control-Bridge\claude
BR draft write <BRIDGE-ID> --status COMPLETED --summary "<kurz>" --actor claude-code --commit
```

**2. Klon `codex` (Executor, kein Push):**

```powershell
cd E:\_DEV\Agent-Control-Bridge\codex
BR draft write <BRIDGE-ID> --status COMPLETED --summary "<kurz>" --actor codex-executor --commit
```

**3. Klon `board` (holt, importiert, pusht):**

```powershell
cd E:\_DEV\Agent-Control-Bridge\board
git pull E:\_DEV\Agent-Control-Bridge\claude main    # oder ...\codex main
BR draft import <BRIDGE-ID> --dry-run                # geplante Schritte pruefen
BR draft import <BRIDGE-ID>
git push                                             # NUR hier, Freigabe April
```

Festgehalten: Push nach GitHub erfolgt ausschliesslich im Klon `board`;
`claude` und `codex` bleiben durch Schicht 1 + 2 gesperrt. Der Pull-Pfad ist
lokal und braucht keinen Push-Zugang des Executors.

## Rueckbau (nur bei Bedarf, durch April)

```powershell
git remote set-url --push origin <echte-URL>
```

und die Deny-Eintraege aus Schicht 1 entfernen.
