# ACB - Uebergabe v14 (Stand 2026-10-06)

**Repo-HEAD bei Erstellung:** ce7170f | **Tests:** 536/536 gruen (524 + 12 aus BRIDGE-0078)
**Fuer den neuen Steuerchat:** docs/ACB-STEUERCHAT-STANDARDSTART.md, docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md (V2.1) und diese Datei. v13 nicht loeschen (Historie).

## 1. Was sich seit v13 geaendert hat

**Neue Erweiterungslinie "Steering Continuity" (BRIDGE-0073 bis 0078), ausgeloest durch April: Dorfschaft
erwartet >1000 Steuerchat-Sitzungen, Uebergabe muss token-sparsam sein.**

- 0073: Abgleich eines extern vorgeschlagenen "Steering Continuity"-Datenmodells (11 Objekte) gegen den realen
  ACB-Mechanismus. Ergebnis: nur `OpenIssue` ohne reales Gegenstueck mit echtem Kontinuitaetsnutzen.
- 0074: Formalisierungsoptionen fuer `OpenIssue` bewertet. **Option A freigegeben** (eigenes Objekt). Befund:
  Option B (Status in `result.yaml` nachtragen) technisch unmoeglich - `result.yaml` ist nach Anlage
  unveraenderlich (`store.py::_write_new`, kein Ueberschreiben).
- 0075: Option A umgesetzt. Neu: `schemas/open-issue.schema.yaml`, Store-Methoden
  `open_issue`/`close_issue`/`list_open_issues`, CLI-Befehlsgruppe `issue open/close/list` (analog
  `task`/`claim`/`run`). 524/524 Tests.
- 0076: T1-Entscheidung MULTI-AGENT-Ausfuehrungsfreigabe. **Option C freigegeben** (MULTI-AGENT bleibt NEIN).
  **Wichtiger Nebenbefund, sicherheitsrelevant:** die Ressourcenregel (0063) wirkt nur klonintern -
  `_check_resource` scannte nur `results/*/claim.json` im eigenen `root`, `claim.json` wurde nie committet,
  `.acb-writer.lock` ist root-lokal und gitignored. **Alle sieben registrierten Projekte** erlauben
  `allowed_machines: [HAM11, DES11]` gleichzeitig - die Luecke betraf nicht nur eine hypothetische
  Mehr-Agenten-Erweiterung, sondern den taeglichen Zwei-Maschinen-Betrieb insgesamt.
- 0077: T1-Entscheidung, wie die Luecke aus 0076 geschlossen wird. **Option B freigegeben** (`claim.json` wird
  versioniert, `claim`/`renew`/`release` committen/pushen kuenftig selbst), **Push-Race-Rollback als
  zwingende Freigabebedingung**, nicht optional.
- 0078: Option B implementiert. `gitops.git_fetch` (neu), neuer Whitelist-`kind="claim"` (exakt
  `results/<id>/claim.json`), `claim`/`renew`/`release` committen+pushen isoliert (bewusst NICHT ueber
  `gitops.git_commit`, siehe §3), Push-Race-Rollback inkl. echter Zwei-Klon-Tests mit bare-Repos. **Seit 0078
  brauchen `claim`/`renew`/`release` Netzwerkzugriff - offline kein Claim moeglich, das ist gewollt.**
  536/536 Tests. **Noch WAITING_FOR_COPY_TO_CONTROL - Board-Aktion (copied+archive) steht noch aus,
  als Erstes nachholen.**

**G5-Blocker aufgeloest:** Der WSL/Worktree-Blocker (siehe v13 §2) ist erledigt - April hat die alten,
verwaisten Worktrees aufgeraeumt. Der zuvor als "gefaehrdet" geltende Commit
`c4407b743ab098d9604a91e60822fce5914ec044` war nie verloren: er ist Tip eines normalen, bereits nach `origin`
gepushten Branches (`codex/AP15-RP2-corrected-review-pending-des11-checkpoint`), kein Worktree-Datenverlust.
Dorfschaft-Projektstand ist laut April inzwischen bei AP16.

**Neu: FK00-Grundlagenkonzept bei Dorfschaft.** April hat mitgeteilt, dass `FK00 - Glossar, Scope und
Authorization` jetzt die Grundlage/den Start aller Dorfschaft-Fachkonzepte bildet, und dass die
ACB-Nutzungslogik dort eingebunden werden muss. **Explizit noch nicht ausgefuehrt** - April wollte das erst
formuliert haben, wenn die Steering-Continuity-Linie hier vollstaendig abgeschlossen ist (siehe §6).

## 2. G-Status
- G0-G4: unveraendert erledigt/in Kraft.
- **G5 (Dorfschaft):** Blocker aufgeloest (siehe oben), aber BRIDGE-0066 (Read-only-Pilot durch Codex) ist
  weiterhin NICHT gestartet. Das ist ein Dorfschaft-Auftrag (`project_id: dorfschaft`, `executor: codex`,
  `controller: openai`) - gehoert in den separaten Dorfschaft-Steuerchat, nicht hierher.
- G6 weiterhin nicht konzipiert, unveraendert zu v13.

## 3. Strukturelle Befunde (wichtig fuer naechste Auftraege, besonders an `claim.py`/`gitops.py`)
- `gitops.git_commit` bricht beim kleinsten Fund ausserhalb der Whitelist fuer den jeweiligen `kind` komplett
  ab (`git status --porcelain` scannt den GANZEN Baum). Deshalb committen `claim`/`renew`/`release` seit 0078
  NICHT ueber `gitops.git_commit`, sondern ueber eine eigene, isolierte Sequenz (`_sync_claim_commit` in
  `claim.py`), die ausschliesslich den exakten Pfad `results/<id>/claim.json` staged - unabhaengig davon, was
  sonst im Baum dirty ist (z. B. ein parallel anstehender Audit-Eintrag aus demselben `claim()`-Aufruf). Bei
  jeder weiteren Aenderung an `claim.py` diese Besonderheit beachten, nicht einfach auf `gitops.git_commit`
  umstellen.
- `claim`/`renew`/`release` brauchen seit 0078 Netzwerkzugriff (fetch+push). Ohne Git-Repo (z. B. hermetische
  Tests) bleibt der Mechanismus no-op wie vor 0078.
- `expected_git_files` (`gitops.py`) kennt jetzt einen vierten relevanten `kind`-Wert `"claim"` neben den
  bestehenden - exakter Pfad, kein Praefix-Match.
- (unveraendert aus v13:) `result.yaml` kennt nur EIN Repository; `.acb-writer.lock` ist weiterhin root-lokal
  und gitignored (unveraendert durch 0078 - das war nicht Teil der Luecke, siehe 0076/0077).

## 4. Arbeitsweise (unveraendert bewaehrt, siehe v12 §3 / v13 §4)
Frischer Klon vor jeder Pruefung, echter Diff statt Selbstauskunft, Haken/HEAD/Suite/Verhalten pruefen, jedes
im Lauf behauptete Befund-Zitat (Dateiname+Zeile) gegen den echten Code nachschlagen, nie selbst ins Repo
schreiben, Governance-Aktionen (copied/archive/run finish) nie selbst ausfuehren.

## 5. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
- MULTI-AGENT bleibt NEIN (0076, Option C freigegeben) - nicht erneut zur Debatte stellen, ausser April bringt
  es selbst wieder auf.
- `OpenIssue` Option A ist die freigegebene, umgesetzte Loesung - nicht nochmal Alternativen pruefen.
- Claim-Sichtbarkeit Option B (inkl. Push-Race-Rollback-Pflicht) ist freigegeben und umgesetzt.
- (unveraendert aus v13:) G3 freigegeben, Klon-Konvention `projects\<projekt-id>`, WETTER-Auftraege gehoeren
  in den Wetter-Steuerchat, Worktree-Entscheidung Dorfschaft lag bei April (jetzt erledigt, siehe §1).

## 6. Offene Punkte - in dieser Reihenfolge
1. **BRIDGE-0078 Board-Aktion** (`copied`+`archive`) - steht noch aus, zuerst erledigen.
2. **Generische Steuerchat-Vorlage** (`docs/ACB-STEUERCHAT-START-GENERISCH-v2.md` /
   `scripts/steuerchat-vorlage.py`) referenziert `OpenIssue` noch NICHT - nur `docs/ACB-STEUERCHAT-ARBEITSWEISE.md`
   wurde in 0075 Teil C aktualisiert, die Vorlage selbst (fuer NEUE Fremdprojekt-Steuerchats) nicht. April hat
   das bewusst zurueckgestellt, bis diese Linie fertig ist - jetzt faellig, braucht einen eigenen kleinen
   ACB-Auftrag (Doku-Aenderung am Kern).
3. **FK00/Dorfschaft:** ACB-Nutzungslogik muss in `FK00 - Glossar, Scope und Authorization`
   (Dorfschaft-Grundlagenkonzept) eingebunden werden. Von April angekuendigt, noch nicht formuliert - siehe §1.
   Das ist inhaltlich eine Dorfschaft-Angelegenheit (gehoert vermutlich eher in den Dorfschaft-Steuerchat als
   hierher), aber die Ausgabe wurde in DIESEM Chat angekuendigt - mit April klaeren, wo das tatsaechlich
   landet, bevor es formuliert wird.
4. (unveraendert aus v13 §6:) Draft-Modus fuer ACB weiterhin offen. Codex-Regel weiterhin nur Schicht 2.
   WinError 10053 weiterhin harmlos. WP 027-029/039-041 weiterhin ohne nachtraeglichen Nachweis.
