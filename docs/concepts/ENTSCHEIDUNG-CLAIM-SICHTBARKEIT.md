# Entscheidung: klonuebergreifende Claim-Sichtbarkeit

**Status:** FREIGEGEBEN (Option B, Push-Race-Rollback als Freigabebedingung), 06.10.2026. BRIDGE-0077, kein Gate.
Fortsetzung der in `ENTSCHEIDUNG-MULTI-AGENT-AUSFUEHRUNG.md` §1 festgestellten Luecke, unabhaengig
von der MULTI-AGENT-Frage (dort Option C, NEIN — hier der taegliche Zwei-Maschinen-Betrieb). Keine
Implementierung, keine Aenderung an `claim.py`/`gitops.py`, keine Projekt-Fachwerte.

## 1. Ist-Stand und Risiko

`_check_resource` (`claim.py:129`) scannt nur `results/*/claim.json` unterhalb des eigenen `root`;
`claim.json` wird nie committet, denn `_cmd_claim` (`cli.py:1044-1054`) ruft `_do_commit` fuer
`claim`/`renew`/`release` nicht auf und `expected_git_files` (`gitops.py:81-116`) kennt fuer diese
Aktionen keinen `kind`. Der Writer-Lock liegt als gitignorierte `.acb-writer.lock` je `root`
(`lock.py:40`). Alle sieben Projektprofile erlauben beide Maschinen gleichzeitig
(`allowed_machines: [HAM11, DES11]`). Zwei Klone desselben Repos/Branches sehen sich damit nicht
und koennen unbemerkt parallel schreiben; der Konflikt faellt erst beim Push auf.

Gegenprobe, was heute **doch** cross-klon sichtbar ist: `tasks/<id>/task.yaml` steht in jeder
Whitelist (`gitops.py:99`), der Auftragsstatus wandert bei `run start`/`run finish` ins Repo.
`results/<id>/<run>/heartbeat.json` ebenso — aber nur dort, denn `run beat` (`cli.py:1068-1073`)
committet nicht: der versionierte `last_seen` ist praktisch der von `run start`, und
`heartbeat_timeout_seconds: 900` (`watcher-policy.yaml`) laeuft aus der Ferne ab, obwohl der Lauf
noch arbeitet.

## 2. Optionen

**A — Fremdpruefung ueber frisch gefetchten Auftragsstatus.** Vor einem neuen Claim `git fetch`
im Store-Root, dann Status aller Auftraege mit gleichem `_resource_key` aus `origin/<branch>`
lesen; nicht-terminaler Status blockiert. Kein neuer Schreibpfad.
- Aufwand **S–M**: `gitops` hat nur `git_pull` (`gitops.py:281`), kein `fetch` — ein Lesehelfer
  kommt dazu, sonst kein Commit, kein Push, kein Schemafeld. Vorteil: nutzt die ohnehin gepushten
  Daten, `claim` bleibt ein Lesevorgang, deckt sich mit der Sofort-Push-Pflicht aus CLAUDE.md.
- Risiko: `task.yaml` hat **keine** Lease/Expiry. Ein Lauf, der ohne saubere Statusaenderung
  abbricht — Usage-Limit und Rechnerwechsel fuehrt CLAUDE.md als Normalfall — blockiert andere
  Klone dauerhaft, bis ein Mensch eingreift; der Watcher setzt `INTERRUPTED` nur mit `--apply`
  und pusht laut `watcher-policy.yaml` nicht.

**B — `claim.json` wird versioniert.** `claim`/`renew`/`release` erhalten einen eigenen
Whitelist-`kind` und committen plus pushen ihre `claim.json`; vorher `fetch` wie in A.
- Aufwand **M** (drei `kind`-Eintraege, Commit/Push im Claim-Pfad, Push-Race-Behandlung, Tests).
  Vorteil: die erprobte Lease-/Expiry-Semantik aus BRIDGE-0061 (`expires_at`, `lease_seconds`,
  Default 3600 s) bleibt **unveraendert** und wird erstmals cross-klon wirksam; abgelaufene
  Claims geben sich weiterhin selbst frei — kein Mensch noetig, anders als bei A.
- Risiko: zwei fast gleichzeitige `claim`-Aufrufe sind beide lokal erfolgreich, der zweite Push
  scheitert non-fast-forward. Fail-closed verlangt dann Rollback des eigenen, nun ungueltigen
  Claims plus harten Fehler; bliebe der lokale Claim stehen, waere die heutige Luecke
  wiederhergestellt. `claim` wird netzabhaengig: offline kein Claim.

**C — Heartbeat als versionierter Lease-Traeger.** Wie A, zusaetzlich committet und pusht
`run beat` seine `heartbeat.json`; die Fremdpruefung liest `last_seen` aus `origin/<branch>` und
wertet `heartbeat_timeout_seconds` aus.
- Aufwand **M** (Whitelist-`kind` fuer `beat`, Commit/Push im Beat-Pfad, Auswertung, Tests).
  Vorteil: liefert A die fehlende Ablaufsemantik, ohne die Claim-Semantik anzutasten; der
  Push-Takt deckt sich mit der Checkpoint-Pflicht aus CLAUDE.md.
- Risiko: die Sperre haengt an einer Annahme ueber den Arbeitsrhythmus. Ein legitimer Schritt ohne
  Beat laenger als 900 s laesst den Lauf aus der Ferne als tot erscheinen — Uebernahme waere
  **zu permissiv**, die gefaehrliche Richtung. Dazu Commit-Last je Checkpoint.

## 3. Fail-Closed-, Generizitaets- und Kosten-Check

| Option | Fail-closed? | Generisch? | Kosten je Claim-Aktion |
|---|---|---|---|
| A | Ja, sogar zu streng: kein stiller Verlust, aber Dauerblockade nach unsauberem Abbruch (Verfuegbarkeitsrisiko, erzeugt Umgehungsdruck). | Ja, liest nur `status` — kein Projekt-Fachwert. | 1 `fetch` bei `claim`; `renew`/`release` unveraendert. |
| B | Ja, **sofern** ein fehlgeschlagener Push den lokalen Claim zurueckrollt und hart scheitert. Ohne Rollback: nein, die Luecke bleibt. | Ja, `claim.json` ist bereits generisch, Whitelist ist `task_id`-parametriert. | 1 `fetch` + 1 `commit` + 1 `push` bei `claim`/`renew`/`release`; offline nicht moeglich. |
| C | Nein, nicht zuverlaessig: der Timeout kann einen lebenden Lauf als tot einstufen und die Ressource freigeben (stiller Parallelzugriff). | Ja, `last_seen` und Timeout sind generisch. | 1 `fetch` bei `claim`, zusaetzlich `commit`+`push` je Heartbeat. |

## 4. Empfehlung

**Option B.** Sie stellt genau das her, was fehlt — Sichtbarkeit — und erfindet dafuer keine
zweite Lebendigkeitssemantik: Lease und Expiry sind seit BRIDGE-0061 erprobt und bleiben
unveraendert, nur ihr Geltungsbereich waechst vom Klon auf das Repository. Damit loest B als
einzige Option den Abbruchfall ohne Menschen, waehrend A dort dauerhaft blockiert und C die
Freigabe an eine Rhythmusannahme bindet, die in der falschen Richtung irrt.
Bedingung der Freigabe: der Push-Race ist Teil der Umsetzung, nicht ein spaeterer Zusatz — ein
`claim`, dessen Push scheitert, muss die lokale `claim.json` entfernen und mit klarem Fehlercode
abbrechen (Vorschlag: bestehender `RESOURCE_CONFLICT`, kein neuer Zustand). Offline bedeutet dann
bewusst: kein Claim. Die `fetch`-Pruefung aus A geht in B ein; C allenfalls spaeter als Lesesignal.

**Nicht Teil dieser Entscheidung:** Implementierung, Aenderungen an
`claim.py`/`gitops.py`/`ENTSCHEIDUNG-RESSOURCENREGEL.md`, G5-Bewertung, Projekt-Adapter-Inhalte.
