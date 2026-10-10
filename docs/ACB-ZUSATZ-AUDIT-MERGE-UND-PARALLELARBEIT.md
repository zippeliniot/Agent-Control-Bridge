## Zusatz für docs/ACB-STEUERCHAT-ARBEITSWEISE.md

### A) Vor WP-Entwurf: Parallelarbeit ausschließen

Bevor ein neuer WP-Entwurf für einen Punkt der vereinbarten Reihenfolge (aktuell
E→F→B→A→C→D) begonnen wird: **immer zuerst prüfen, ob dieser Punkt nicht
bereits von einer anderen Sitzung (Browser-Claude, anderer Steuerchat,
Claude Code direkt) angelegt/bearbeitet wurde.**

```
bridge board
bridge task show BRIDGE-0<nächste freie ID>
```

Grund (Vorfall 10.10.2026): BRIDGE-0104 wurde unabhängig von zwei Sitzungen
inhaltlich nahezu identisch entworfen — eine davon hatte den Auftrag bereits
vollständig durchlaufen (`task_create → run_start → Teil A/B → run_finish`),
bevor die andere ihren Entwurf auslieferte. Kein Schaden entstanden, aber
vermeidbarer Doppelaufwand und ein zusätzlicher Merge-Konflikt in
`audit/audit.jsonl`.

### B) Merge-Konflikte in `audit/audit.jsonl` (Append-only-Logdatei)

`audit/audit.jsonl` ist append-only: jede Zeile ein unabhängiges,
abgeschlossenes JSON-Event. Bei einem Merge-Konflikt in dieser Datei gilt
**immer**: beide Seiten enthalten echte, gültige Events — niemals eine Seite
verwerfen.

**Standardverfahren:**
1. Konfliktmarker zählen und lokalisieren:
   ```powershell
   (Select-String -Path audit\audit.jsonl -Pattern "^(<<<<<<<|=======|>>>>>>>)").Count
   Select-String -Path audit\audit.jsonl -Pattern "^(<<<<<<<|=======|>>>>>>>)"
   ```
2. Den Inhalt um die Marker herum ansehen (nicht blind auflösen) —
   `Get-Content ... | Select-Object -Index (<Bereich>)`.
3. Nur die Marker-Zeilen selbst entfernen, alle Event-Zeilen auf beiden Seiten
   behalten:
   ```powershell
   (Get-Content audit\audit.jsonl) | Where-Object { $_ -notmatch '^(<<<<<<<|=======|>>>>>>>)' } | Set-Content audit\audit.jsonl -Encoding UTF8
   ```
4. Committen, pushen.

Nie `git checkout --ours`/`--theirs` auf diese Datei anwenden — das würde
echte Audit-Events der jeweils anderen Seite löschen.
