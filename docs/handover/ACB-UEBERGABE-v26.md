# ACB-Übergabe v26

**Letzter verifizierter HEAD:** `84c0203` (BRIDGE-0104 ARCHIVED, gepusht,
bestätigt durch reale PowerShell-Ausgabe des Nutzers — kein VM-Fetch).

## §1 Reihenfolge-Status (E→F→B→A→C→D)

| Punkt | Inhalt | Status |
|---|---|---|
| E | BRIDGE-0103 Qualitätsrahmen Übergaben | ARCHIVED |
| F | BRIDGE-0104 wp-lint.py Erweiterung (Prüfungen 5-7) | **ARCHIVED** (HEAD 84c0203) |
| B | Decision-Log Ablageform + CLI/Store | **offen — nächster Schritt** |
| A | Context-Assembler-Schema | offen |
| C | Routing-Feld | offen |
| D | Symbol-Graph Indexer | offen |

## §2 Vorfall heute (10.10.2026): Parallelarbeit zweier Sitzungen auf BRIDGE-0104

Eine andere Sitzung (`created_by: browser-claude`) hat BRIDGE-0104 unabhängig
von diesem Steuerchat entworfen und **vollständig durchlaufen lassen**
(`task_create → run_start → Teil A/B → run_finish`), bevor dieser Steuerchat
seinen eigenen (inhaltlich fast identischen) Entwurf auslieferte. Der Entwurf
dieses Steuerchats wurde verworfen, die bereits durchgelaufene Version wurde
regulär kopiert und archiviert (`task copied` → `task archive`).

**Nebenwirkung:** Merge-Konflikt in `audit/audit.jsonl` (zwei parallele
Append-Vorgänge an derselben Stelle). Gelöst durch Beibehaltung beider Seiten,
nur Entfernen der Git-Konfliktmarker — vollständiges Verfahren jetzt in
`docs/ACB-STEUERCHAT-ARBEITSWEISE.md` dokumentiert (siehe Zusatz, von April
einzufügen).

**Offene, von der anderen Sitzung getroffene Entscheidung:** Prüfung 5
(Issue-Referenz-Check in wp-lint.py) wurde als **Fehler/Exit 1** umgesetzt.
April hat nach Rückfrage direkt `task archive` ausgeführt, ohne explizit zu
widersprechen — als akzeptiert gewertet, aber nicht wortwörtlich bestätigt.
Bei Zweifel: nachfragen, nicht als endgültig behandeln.

## §3 Neue Pflichtregeln aus diesem Vorfall (zusätzlich zu v25 §3)

1. **Vor jedem neuen WP-Entwurf:** `bridge board` / `task show` prüfen, ob der
   nächste Punkt der Reihenfolge nicht bereits von einer anderen Sitzung
   bearbeitet wird (verhindert Doppelarbeit wie bei BRIDGE-0104).
2. **`audit/audit.jsonl`-Merge-Konflikte:** immer beide Seiten behalten,
   niemals `--ours`/`--theirs`, nur Marker-Zeilen entfernen. Vollständiges
   Verfahren siehe Zusatzdokument.

## §4 Weiterhin gültig (aus v25, nicht erneut verifizieren)

- Keine Git-Mechanik in der Steuerchat-VM — alles über Claude Code/PowerShell.
- MODELL/DENKSTUFE-Zeile Pflicht in jedem Claude-Code-Auftragsblock.
- Kurze PowerShell-Verifikationsbefehle (Select-String/Measure-Object), keine
  vollen Dumps.
- Governance-Aktionen nur durch Nutzer/Claude Code, nie durch den Steuerchat
  selbst.
- Kontext-Monitoring-Pflicht (proaktiv melden, rechtzeitig Übergabe erstellen).
- Leseanweisung: Pflichtdokumente vollständig bis zum Ende lesen, „bei Bedarf"
  ≠ überspringbar.

## §5 Noch nicht ins Repo übernommen (Stand jetzt)

- `docs/ACB-ZUSATZ-AUDIT-MERGE-UND-PARALLELARBEIT.md` (gerade ausgeliefert,
  siehe §3 — Inhalt dort vollständig, nur Platzierung in
  `ACB-STEUERCHAT-ARBEITSWEISE.md` offen)
- Diese v26-Übergabe selbst

## §6 Nächster Schritt

Punkt B (Decision-Log Ablageform + CLI/Store-Anbindung) — Grundlage:
`schemas/decision.schema.yaml` (aus BRIDGE-0097) existiert bereits, aber ohne
CLI/Store-Anbindung (bewusste Scope-Grenze damals). Vor WP-Entwurf: Parallelarbeit
ausschließen (§3 Punkt 1).
