# BRIDGE-0077 - Haertungsentscheidung: klonuebergreifende Claim-Sichtbarkeit

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0077 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Teile (alte Nummern) | keine (neuer Auftrag, kein Buendel) |
| Rechte | WORKTREE_WRITE, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / HIGH** - Sicherheitsfall (Fortsetzung der in BRIDGE-0076 §1 festgestellten Luecke), daher HIGH statt MEDIUM. |
| Modellwechsel zum Vorgaenger | NEIN (BRIDGE-0076 lief ebenfalls auf Claude Opus 5 / HIGH) |
| depends_on | BRIDGE-0076 (ARCHIVED) |
| Gate | keines (reine Entscheidung, kein G2/G3/G4-Scope beruehrt) |
| stop_conditions | CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0077` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag

**Hintergrund:** `docs/concepts/ENTSCHEIDUNG-MULTI-AGENT-AUSFUEHRUNG.md` §1 (BRIDGE-0076, verifiziert) stellt fest: die Ressourcenregel (BRIDGE-0063) wirkt nur klonintern. `_check_resource` (`claim.py`) scannt ausschliesslich `results/*/claim.json` im eigenen `root`; `claim.json` wird von `claim`/`renew`/`release` nie committet (diese Befehle rufen `gitops.git_commit` nicht auf, anders als `task_create`/`run_start`/`run_finish`), `.acb-writer.lock` ist root-lokal und gitignored. Jedes der sieben registrierten Projekte erlaubt beide Maschinen gleichzeitig (`allowed_machines: [HAM11, DES11]`, ausnahmslos). Zwei Klone desselben Repos/Branches auf unterschiedlichen Maschinen sehen sich damit heute nicht und koennen unbemerkt parallel schreiben - unabhaengig von der MULTI-AGENT-Frage, bereits im taeglichen Betrieb relevant.

**Ziel:** Eine Entscheidungsdatei, die festlegt, WIE ein Claim maschinenuebergreifend sichtbar gemacht wird, ohne die bestehende Lease-/Expiry-Semantik (BRIDGE-0061) zu verlieren und ohne das Fail-Closed-Prinzip aufzuweichen. Keine Implementierung, keine Aenderung an `claim.py`/`gitops.py`.

**Scope:** Neu: `docs/concepts/ENTSCHEIDUNG-CLAIM-SICHTBARKEIT.md` (max. 80 Zeilen). Sonst nichts. Kein Code, kein `schemas/`-Eintrag.

1. Ist-Stand/Risiko in 3-5 Saetzen benennen (siehe Hintergrund oben, mit Fundstellen).
2. Mindestens zwei Haertungsoptionen ausarbeiten, je mit T-Shirt-Groesse, Vor-/Nachteilen, Risiken:
   - **A - Fremdpruefung ueber frisch gefetchten `task.yaml`-Status:** vor einem neuen Claim `git fetch origin` im Store-Root, dann Status anderer Auftraege mit gleichem `_resource_key` aus `origin/<branch>` (nicht nur lokal) lesen; nicht-terminaler Status blockiert. Kein neuer Commit/Push-Schritt bei `claim`/`renew`/`release`. Ausdruecklich zu bewerten: `task.yaml` kennt keine Lease/Expiry wie `claim.json` - ein abgebrochener Lauf ohne sauberen Status-Uebergang wuerde andere Klone ggf. dauerhaft blockieren statt automatisch nach Ablauf freizugeben.
   - **B - `claim.json` wird Teil der Commit-Whitelist:** `claim`/`renew`/`release` committen und pushen kuenftig selbst (heute tun sie das nicht). Bestehende Lease-/Expiry-Semantik bleibt vollstaendig erhalten und wird erstmals cross-klon sichtbar. Ausdruecklich zu bewerten: zwei nahezu gleichzeitige `claim`-Aufrufe auf unterschiedlichen Maschinen koennen beide lokal erfolgreich sein, bevor einer pusht - der zweite Push scheitert (non-fast-forward) und braucht eine neue Fehlerbehandlung (Rollback des eigenen, dann ungueltigen Claims), die es heute nicht gibt.
   - Optional weitere Option(en), falls im Rahmen der Pruefung erkennbar.
3. Fuer jede Option explizit pruefen: bleibt das Fail-Closed-Prinzip erhalten (ein unerkannter Fremd-Claim darf nie zu stillem Datenverlust fuehren)? Bleibt die Loesung generisch (kein Projekt-Fachwert in `claim.py`/`gitops.py`)? Netzwerk-/Performance-Kosten je Claim-Aktion?
4. Empfehlung mit Begruendung; Status ENTWURF, Freigabe durch April ausstehend.
5. Ausdruecklich NICHT Teil dieses Auftrags: Implementierung der empfohlenen Option, Aenderung an `claim.py`/`gitops.py`/`ENTSCHEIDUNG-RESSOURCENREGEL.md`, G5-Bewertung, Projekt-Adapter-Inhalte.

**Tests:** Keine.

- [x] Ist-Stand/Risiko mit Fundstellen benannt
- [x] Mindestens zwei Haertungsoptionen (A, B, ggf. weitere) mit T-Shirt-Groesse, Vor-/Nachteilen, Risiken
- [x] Fail-Closed-, Generizitaets- und Kosten-Check je Option
- [x] Empfehlung mit Begruendung, Status ENTWURF
- [x] Kein Code/Schema geaendert
