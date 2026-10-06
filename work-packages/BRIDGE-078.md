# BRIDGE-0078 - Implementierung klonuebergreifende Claim-Sichtbarkeit (Option B)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0078 |
| project_id | agent-control-bridge |
| Typ / Klasse | Buendel / FEATURE |
| Teile (alte Nummern) | keine (neuer Auftrag, kein Buendel-Altbestand) |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - Ressourcenregel-Erweiterung + Push-Race-/Ausfalltests, ein Bereich (Vorbild BRIDGE-0063). |
| Modellwechsel zum Vorgaenger | JA (BRIDGE-0077 war Claude Opus 5 / HIGH, T1-Entscheidung; dies ist T2-Implementierung) |
| depends_on | BRIDGE-0077 (ARCHIVED) |
| Gate | keines |
| stop_conditions | CONCEPT_CONFLICT, SCOPE_VIOLATION |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0078` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

**Teile strikt nacheinander (A, B, C). Pro Teil: Haken setzen, Commit, Push. Scheitert ein Teil: STOPP (BLOCKED), spaetere Teile nicht beginnen.**

**Vorbedingung (vor Teil A pruefen, nicht annehmen):** `docs/concepts/ENTSCHEIDUNG-CLAIM-SICHTBARKEIT.md` muss Status `FREIGEGEBEN (Option B, ...)` tragen. Steht dort noch `ENTWURF`: STOPP, `CONCEPT_CONFLICT`.

## Auftrag

**Ziel:** Option B aus `ENTSCHEIDUNG-CLAIM-SICHTBARKEIT.md` umsetzen: `claim.json` wird versioniert, `claim`/`renew`/`release` committen und pushen sich selbst, `_check_resource` prueft zusaetzlich gegen den frisch gefetchten `origin`-Stand. Die Lease-/Expiry-Semantik aus BRIDGE-0061 bleibt unveraendert. Push-Race-Rollback ist **Pflichtbestandteil**, nicht nachtraeglich: scheitert der Push, wird die lokale `claim.json` entfernt und mit `RESOURCE_CONFLICT` hart abgebrochen.

### Teil A - `git fetch` + Whitelist-Erweiterung

**Scope:** `src/bridge/gitops.py`, `tests/test_gitops.py`.

1. Neue Funktion `git_fetch(repo_root) -> dict` analog zu `git_pull` (`gitops.py:281`): `git -C <root> fetch origin <branch>`, Fehler fail-closed (kein stiller Erfolg bei Netzwerkfehler).
2. `expected_git_files` (`gitops.py:81ff`) um einen neuen `kind` erweitern (Vorschlag: `"claim"`, gemeinsam fuer `claim`/`renew`/`release`, da alle drei ausschliesslich `results/<task_id>/claim.json` beruehren) - exakter Pfad, kein Praefix-Match.
**Tests:** `python -m unittest tests.test_gitops`, dann volle Suite EINMAL.
- [ ] `git_fetch` implementiert, Fehlerfall getestet
- [ ] Neuer `kind` fuer Claim-Aktionen in `expected_git_files`, genau `results/<task_id>/claim.json` als erlaubter Pfad

### Teil B - Commit/Push im Claim-Pfad + Push-Race-Rollback

**Scope:** `src/bridge/claim.py`, `src/bridge/cli.py`, `tests/test_claim.py`, `tests/test_cli.py` (Dateinamen gegen echten Bestand pruefen, nicht annehmen).

1. `_check_resource` (`claim.py:129`) erweitern: vor der lokalen Pruefung `git_fetch` aufrufen, dann zusaetzlich `origin/<branch>`-Stand der `tasks/*/task.yaml`-Status fuer denselben `_resource_key` lesen (die in BRIDGE-0077 §1 genannte Gegenprobe) ODER, falls einfacher und ausreichend, ausschliesslich ueber die jetzt versionierten `claim.json` aus `origin/<branch>` pruefen - Entscheidung liegt bei der Umsetzung, solange fail-closed und Ergebnis mit Lease/Expiry konsistent bleibt. Keine Aenderung der Lease-/Expiry-Werte selbst.
2. `claim`/`renew`/`release` (`_cmd_claim`, `cli.py:1044ff`) committen und pushen nach erfolgreicher lokaler Operation (analog `_do_commit`, `cli.py:277`, neuer `kind` aus Teil A).
3. **Push-Race-Rollback (Pflicht):** schlaegt der Push fehl (non-fast-forward oder sonstiger Git-Fehler), wird die soeben lokal geschriebene `claim.json` entfernt (bei `claim`: komplett geloescht; bei `renew`: auf den vorherigen Stand zurueckgesetzt, falls rekonstruierbar, sonst ebenfalls harter Fehler ohne Teilzustand) und `ClaimError` mit `RESOURCE_CONFLICT` geworfen - kein stiller Erfolg, kein haengender lokaler Claim ohne Entsprechung im Repo.
4. `release` bei Pushfehler: lokale Freigabe ebenfalls zurueckrollen (alten `claim.json`-Inhalt wiederherstellen) statt inkonsistenten Zustand zu hinterlassen.
**Tests:** gezielte Push-Race-Simulation (z. B. zweiter lokaler Klon/Remote-Vorsprung erzeugen, Push bewusst scheitern lassen, Rollback + Fehlercode pruefen) fuer `claim`, `renew`, `release` je einzeln. Dann `python -m unittest tests.test_claim tests.test_cli`, dann volle Suite EINMAL.
- [ ] `claim`/`renew`/`release` committen und pushen nach lokalem Erfolg
- [ ] Push-Race-Simulation je Aktion: Rollback + `RESOURCE_CONFLICT`, kein haengender Zustand (Test)
- [ ] Cross-Klon-Sichtbarkeit nachgewiesen (zwei Store-Instanzen, zweiter `claim` auf denselben `_resource_key` nach gepushtem ersten Claim schlaegt fehl)

### Teil C - Dokumentations-Minimalverweis

**Scope:** NUR `src/bridge/claim.py` Modul-Docstring (Kopf der Datei) und `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 4. Sonst nichts.

1. Docstring von `claim.py` um einen Satz ergaenzen: `claim.json` ist seit BRIDGE-0078 versioniert und cross-klon wirksam (vorher klonlokal, siehe `ENTSCHEIDUNG-CLAIM-SICHTBARKEIT.md`).
2. In `ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 4: ein bis zwei Saetze, dass `claim`/`renew`/`release` jetzt Netzwerkzugriff brauchen (offline kein Claim moeglich).
**Tests:** keine.
- [ ] Docstring-Ergaenzung in `claim.py`
- [ ] Kurzer Verweis in `ACB-STEUERCHAT-ARBEITSWEISE.md` Abschnitt 4, sonst keine Aenderung

## Abschluss

1. Volle Suite EINMAL, nur die letzten 3 Zeilen zeigen.
2. `git status` sauber, dann Abschluss wie im Slash-Befehl.
- [ ] Volle Suite gruen
