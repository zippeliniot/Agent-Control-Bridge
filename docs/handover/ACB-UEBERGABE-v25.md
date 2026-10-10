# ACB-Übergabe v25

**Letzter verifizierter HEAD (Steuerchat-Sitzung v24, vor dieser Sitzung):** `3a1c825`
(BRIDGE-0103 ARCHIVED, gepusht). **Diese Sitzung hat keinen neuen Fetch/Clone
durchgeführt** (Steuerchat-VM führt keine Git-Operationen aus, siehe §7) —
der nächste Chat muss den aktuellen HEAD selbst über die lokale Maschine
(Claude Code / PowerShell) feststellen, nicht annehmen.

## §1 Reihenfolge-Status (E→F→B→A→C→D)

| Punkt | Inhalt | Status |
|---|---|---|
| E | BRIDGE-0103 Qualitätsrahmen Übergaben | **ARCHIVED** (HEAD 3a1c825) |
| F | BRIDGE-0104 wp-lint.py Erweiterung | **WP geschrieben, noch NICHT staged/delivered** |
| B | Decision-Log Ablageform + CLI/Store | offen |
| A | Context-Assembler-Schema | offen |
| C | Routing-Feld | offen |
| D | Symbol-Graph Indexer | offen |

## §2 Konkreter Stand von Punkt F (BRIDGE-0104)

- `work-packages/BRIDGE-104.md` ist **vollständig geschrieben** (lokal in dieser
  Steuerchat-Sitzung, noch nicht an den Nutzer ausgeliefert).
- Inhalt: wp-lint.py (BRIDGE-0102) um 3 Prüfungen erweitern:
  1. Issue-Referenzen auflösbar (Existenzcheck gegen `open-issues/<project>/`)
  2. BRIDGE-Referenz + Abschlusswort ohne `tasks/<id>/task.yaml` → **Warnung**,
     Exit bleibt 0 (ISSUE-0006-Muster generalisiert)
  3. Fehlende `## Akzeptanzkriterien`-Sektion oder fehlender Scope-Hinweis → Fehler, Exit 1
- Bewusst NICHT Teil: keine `decision_id`-Referenzprüfung (kein Store vorhanden),
  keine Prüfung von Übergabedateien gegen den Qualitätsrahmen (andere Dateiklasse).
- **Noch zu tun, bevor Auslieferung an den Nutzer:**
  1. Staging-YAML `tasks/incoming/BRIDGE-0104.yaml` erstellen
     (`expected_head: EXPECTED_HEAD`, `model: Claude Sonnet 5`,
     `reasoning_level: MEDIUM`, `permissions: [WORKTREE_WRITE, TEST_EXECUTION,
     GIT_COMMIT, GIT_PUSH]`, `allowed_paths: [scripts/wp-lint.py,
     tests/test_wp_lint.py, work-packages/BRIDGE-104.md]`)
  2. Lokalen Selbstcheck laufen lassen:
     `.venv/bin/python scripts/wp-lint.py --wp work-packages/BRIDGE-104.md --staging tasks/incoming/BRIDGE-0104.yaml`
  3. Erst bei "OK" beide Dateien per Datei-Auslieferung an den Nutzer geben
  4. WO:-PowerShell-Platzierungsbefehle + korrigierter Claude-Code-Pflichtblock
     (siehe §4) mitgeben

## §3 Verbindliche Lektionen aus dieser Sitzung (NICHT erneut verifizieren, nur anwenden)

1. **Keine Git-Mechanik in dieser Steuerchat-VM.** Clone/Pull/Push/Fetch führt
   ausschließlich der Nutzer über Claude Code auf seiner eigenen Maschine aus
   ("alles durch claude code nicht über vm da es immer zu fehlern führt").
   Der Steuerchat liest lokale Dateien nur als Referenz, niemals als Behauptung
   über den aktuellen Remote-Stand.
2. **Jeder Claude-Code-Auftragsblock MUSS explizit** beginnen mit:
   `MODELL: <Modell> / DENKSTUFE: <Stufe>` — fehlt diese Zeile, ist der Block
   unvollständig (Pflicht aus ARCHITECTURE.md §13 / PROJEKTKONZEPT.md §27/§34).
3. **PowerShell-Verifikationsbefehle kurz halten** — `Select-String`,
   `Measure-Object`, `Select-Object -Last N`, nie volle Datei-Dumps oder volle
   Testläufe ungekürzt ausgeben lassen.
4. **Governance-Aktionen** (`task copied`, `task archive`, `run finish`)
   führt ausschließlich der Nutzer/Claude Code aus, niemals der Steuerchat
   selbst — der Steuerchat liefert nur die Befehle und prüft danach die
   zurückgemeldete Ausgabe.

## §4 Korrigiertes Pflichtblock-Format für Claude-Code-Aufträge

```
MODELL: Claude Sonnet 5 / DENKSTUFE: <LOW|MEDIUM|HIGH>

Pflichtblock (unübersehbar, nicht verhandelbar):
1. Jede Zustandsänderung ausschließlich über die Bridge-CLI, nie direktes
   Bearbeiten von Store-Dateien.
2. GIT_PUSH steht im Berechtigungsprofil — am Ende git push ausführen.

Führe Auftrag BRIDGE-0xxx aus: lies .claude/commands/acb-auftrag.md und
befolge es wortgenau.
```

## §5 Kernbefund v24 (weiterhin gültig, nicht erneut verifizieren)

Die externe Prüfung (10.10.2026) des Drei-Schichten-Modells bewertete einen
bereits überholten Zwischenstand. Die tatsächlich verbleibenden offenen Punkte
sind A–D oben (plus die aus der Prüfung übernommenen E/F). Details siehe
`docs/concepts/ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md` §2/§3 — dort
steht die vollständige Vergleichstabelle; nicht neu aufrollen, außer bei
konkretem Zweifel an einer einzelnen Zeile.

## §6 Warum dieser Übergabe-Chat jetzt

Kontext dieser Sitzung ist durch vollständiges Pflichtlektüre-Protokoll
(Standardstart-Prozedur: alle Primärquellen, Schemas, Konzepte vollständig
lesen) weit gefüllt. Diese Übergabe fasst den Stand zusammen, damit ein
Folgechat nicht erneut alle oben genannten Punkte verifizieren muss.

## §7 Nicht von selbst anfangen bei

- §3 und §5 nicht erneut verifizieren, außer bei konkretem Zweifel an einer
  einzelnen Aussage.
- Nicht erneut nach GitHub-Zugangsdaten oder Git-Login-Anweisungen fragen —
  das ist bereits eingerichtet und funktioniert (siehe Nutzer-Workflow in
  dieser Sitzung).

## §8 Nächster Schritt

Punkt F fertigstellen (Staging-YAML + Selbstcheck + Auslieferung, siehe §2),
dann B → A → C → D in dieser Reihenfolge.
