# ACB - Uebergabe v21 (Stand 2026-10-09)

**Repo-HEAD bei Erstellung:** `01beb76b866c61245d5bc36247a8bc56dedafbfd` (`01beb76`) | **Tests:**
594/594 - zuletzt in dieser Reihe unabhaengig frisch nachgelaufen (vor BRIDGE-0100/v20, s.u.);
seither keine Code-Aenderung, nur die v20-Dokumentationsdatei selbst und diese Datei (reine
Dokumentation, kein Code).

**Fuer den neuen Steuerchat:** `docs/ACB-STEUERCHAT-STANDARDSTART.md`, diese Datei. v19 **und**
v20 nicht loeschen (Historie, v20 ist die unmittelbare Vorsitzung).

**Anlass dieser Version:** Zwei getrennte Steuerchat-Sitzungen haben parallel an der naechsten
Uebergabe gearbeitet. Die eine (direkt am Repo, Windows-Seite) hat v20 bereits real gepusht
(`01beb76`, Stand BRIDGE-0093 bis -0100 + drei neue offene Punkte). Die andere (dieser Chat, auf
Bitte von April: "aktuellen Stand ermitteln") hatte parallel einen eigenen Entwurf vorbereitet, der
**nicht mehr als v20 verwendet wird** - er haette die bereits gepushte, inhaltlich andere v20
stillschweigend ueberschrieben. v21 fuehrt beide zusammen: die real gepushten offenen Punkte aus
v20 **plus** einen Governance-Befund aus diesem Chat, der in v20 nicht vorkommt, **plus** (neu in
dieser Fassung, Abschnitt 4) eine Bewertung des Drei-Schichten-Modells samt Umsetzungsplan, auf
ausdrueckliche Anweisung von April. v21 selbst ist bisher **nicht gepusht** - naechste reale
Versionsnummer ist weiterhin v21, kein Sprung auf v22.

## 1. Aus v20 uebernommen (real gepusht, nicht hier neu geprueft)

BRIDGE-0093 bis BRIDGE-0100 sind `ARCHIVED`, gepusht, Details siehe v20 §1 - hier nicht wiederholt.
Drei offene Punkte aus v20 §2, **vollstaendig uebernommen, nicht umgesetzt**:

- **2a. Projekt-ID-Feld im Stammdaten-Block:** zeigt rohe `project_id` als Freitext, waehrend die
  bestehende Filter-Dropdown bewusst `task_prefix` zeigt (`cli.py:_board_project()`) - verwirrend,
  kein Datenfehler. Naechster Schritt (mit April abgestimmt, noch nicht umgesetzt): Dropdown mit
  echten `project_id`-Werten, neuer lesender Endpunkt auf Basis von
  `profiles.list_profiles(store.root)` (`src/bridge/profiles.py:127`, existiert, bisher nicht über
  die Web-UI-API exponiert), `ps-projekt` von `<input>` auf `<select>` umstellen.
- **2b. Hamburger-Menue mit Beschreibungsseiten:** gewuenscht, Umfang **ungeklaert** (welche
  Inhalte, reine Links vs. eigene gerenderte Seiten, Layout-Position) - zuerst klaeren, bevor ein
  Auftrag entsteht.
- **2c. `machine: vm` in Audit-Eintraegen (BRIDGE-0093 bis -0100):** erklaert, kein Bug
  (`platform.node()`-Fallback ohne `--machine`-Flag, da der vorherige Steuerchat selbst per CLI in
  dieser Cloud-Sitzung ausgefuehrt hat, nicht via Claude Code auf HAM11/DES11). Nicht rueckwirkend
  korrigierbar (`audit/audit.jsonl` append-only). Vorschlag aus v20, **noch nicht in
  `ACB-STEUERCHAT-ARBEITSWEISE.md` uebernommen:** Steuerchat soll bei eigener CLI-Ausfuehrung
  immer ein explizites `--machine`-Flag setzen (z. B. `--machine browser-claude`).

**Naechste freie BRIDGE-ID laut v20 §3: BRIDGE-0101** - durch nichts in diesem Chat veraendert.

## 2. Befund aus diesem Chat, in v20 NICHT dokumentiert (weiterhin offen)

**`BRIDGE-0092` ist kein realer Auftrag.** Beleg (unveraendert gueltig, HEAD seither nur um den
v20-Dokumentationscommit gewachsen, keine Code-Aenderung): `tasks/BRIDGE-0092/` existiert nicht,
`work-packages/BRIDGE-092.md` existiert nicht, nie in der Git-Historie angelegt. Der echte
Code-Commit (`7fa95f9658c0c15c81712d117e73261fa2a190aa`, "gitops/cli: --commit-Flag fuer bridge
issue open/close") lief ohne den sonst durchgaengigen `task create`/`run start`/`run
finish`/`copied`/`archive`-Zyklus. Die Nummer wird trotzdem in drei Stellen als abgeschlossener
Auftrag zitiert: `docs/handover/ACB-UEBERGABE-v19.md` §1/§2,
`open-issues/agent-control-bridge/agent-control-bridge-ISSUE-0003.yaml: note`,
`work-packages/BRIDGE-097.md`.

**Drei moegliche Wege, keiner gewaehlt:**
1. Rueckwirkend formal nachbuchen (`tasks/BRIDGE-0092/task.yaml` anlegen, Status direkt
   `ARCHIVED`, Vermerk "nachtraeglich formalisiert") - ohne Praezedenz in ACB.
2. Als `OpenIssue` dokumentieren (analog `ISSUE-0001` bis `-0004`), die drei Stellen unveraendert
   lassen.
3. Beides: Issue anlegen und im Issue-Text klarstellen, dass keine Nachbuchung erfolgt.

## 3. G-Status
Unveraendert zu v16-v20 (G0-G5, G6 weiterhin nicht konzipiert).

## 4. Drei-Schichten-Modell: Status, Bewertung und Umsetzungsplan (neu in dieser Fassung)

**Ausgangsfrage (April, dieser Chat):** Ist das Drei-Schichten-Konzept (Decision-Log /
Symbol-/Datei-Graph / Vektor-RAG-Archiv) als ausfuehrbarer Auftrag abgebildet?

**Befund (frisch, HEAD `01beb76`):** Nein. Es existieren nur das Entscheidungsdokument
(`docs/concepts/ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md`, Status "ENTWURF -
ENTSCHEIDUNG AUSSTEHEND") und die Spezifikation (`docs/concepts/
DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md`, BRIDGE-0094). Letztere haelt in §6 ("Was das NICHT
ist") ausdruecklich fest: keine Aenderung an `CLAUDE.md`/`project.schema.yaml`/`task.schema.yaml`,
kein Indexer-Code, kein Symbol-Graph-Code, kein Context-Assembler-Code - bewusster Scope, kein
Versehen. Reale, archivierte Vorbereitungsauftraege decken jeweils nur einen Teilaspekt:

| BRIDGE-ID | Status | Deckt ab |
|---|---|---|
| 0093 | ARCHIVED | Mehrprojekt-RAG-Vorbedingung (Subfolder-Konvention, kein Code noetig) |
| 0094 | ARCHIVED | Die Architektur-Spezifikation selbst (Begriffstabelle, Edge-Typen, Routing-Idee) |
| 0096 | ARCHIVED | Governance-Entscheidung: kein neues Gate noetig |
| 0097 | ARCHIVED | Nur `schemas/decision.schema.yaml` - bewusst ohne CLI-/Store-Anbindung |
| 0098 | ARCHIVED | Tree-sitter-Spike (Machbarkeit fuer PHP/JS/PowerShell bestaetigt) |

**Bewertung von April (dieser Chat, woertlich sinngemaess):** Das RAG-Konzept allein ist nicht
funktionsfaehig als verlaessliche Quelle fuer die Steuerchat-Uebergabe - erst in Kombination mit
den beiden oben genannten Ergaenzungen (Decision-Log, Symbol-/Datei-Graph) erreicht die Uebergabe
das angestrebte hohe Qualitaetsniveau. Diese Einschaetzung deckt sich mit der Spezifikation
selbst (`DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md` §1, Quellenprioritaet, woertlich): "Decision-
Log und Symbol-Graph sind gleichrangig strukturiert und haben beide Vorrang vor einem
Vektor-RAG-Archivtreffer; ein Archivtreffer bleibt ungeprueftes Hintergrundmaterial, bis er in
eine der beiden strukturierten Schichten uebernommen ist." Ohne die beiden strukturierten
Schichten (und ohne den Context-Assembler, der sie zusammenfuehrt und priorisiert, §3) hat ein
RAG-Treffer keine verlaessliche Einordnung gegenueber Entscheidungen/Code-Abhaengigkeiten - er
bleibt isoliertes, ungeprueftes Material. Das RAG-Archiv ist damit nicht als eigenstaendig
"fertige" Schicht zu verstehen, sondern als nachrangiger Fallback innerhalb eines Systems, das
erst mit allen drei Schichten funktioniert.

**Umsetzungsplan (Vorschlag, von April noch zu bestaetigen - Reihenfolge, nicht eigenmaechtig
final festgelegt):**

1. **Decision-Log operationalisieren:** CLI-/Store-Anbindung fuer `schemas/decision.schema.yaml`
   (Schema existiert aus BRIDGE-0097, bewusst ohne Anbindung geliefert - offene Folgefrage,
   benannt in `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH-V2.md` §5 und Spezifikation §5). Ohne
   diesen Schritt bleibt die erste der beiden primaeren, strukturierten Schichten nur Schema ohne
   Betrieb.
2. **Symbol-/Datei-Graph - Trägerfrage klaeren, dann Indexer beauftragen:** Spezifikation §5 nennt
   "wer baut/pflegt den Symbol-/Datei-Graph (Claude Code, Codex, eigenes Tooling)" ausdruecklich
   als offen, nicht Teil der Spezifikation. Erst nach dieser Klaerung: Indexer-Auftrag, aufbauend
   auf dem bereits abgeschlossenen Tree-sitter-Spike (BRIDGE-0098 - Machbarkeit fuer PHP/JS/
   PowerShell bereits bestaetigt, kein technischer Blocker mehr offen).
3. **Context-Assembler-Schema entwerfen:** aktuell nur Sketch (Spezifikation §3: `session_delta`,
   Revisionsbindung, Fail-soft-Rueckschreibung ins Decision-Log) - kein Schema-Entwurf. Dieser
   Schritt fuehrt Pflichtkontext + beide strukturierten Schichten zusammen und schreibt das
   Sitzungs-Delta zurueck.
4. **Routing-Feld entscheiden:** welches Schema-Feld (`project.schema.yaml`/`task.schema.yaml`)
   steuert, welche Schicht eine konkrete Anfrage bedient (Spezifikation §2) - bisher offen.
5. **Erst danach ist das Vektor-RAG-Archiv als vollwertiger, eingeordneter Fallback nutzbar** -
   vorher liefert ein RAG-Treffer laut Spezifikation §1 nur ungeprueftes Hintergrundmaterial ohne
   verlaessliche Rangordnung gegenueber Decision-Log/Symbol-Graph. Reihenfolge 1-4 vor 5 ist damit
   keine willkuerliche Priorisierung, sondern Voraussetzung dafuer, dass RAG-Treffer ueberhaupt
   sinnvoll eingeordnet werden koennen.

Diese Reihenfolge ist ein Vorschlag aus diesem Chat, keine Entscheidung - sie wird April zur
Bestaetigung vorgelegt (Abschnitt 5, Punkt 1 unten), nicht eigenmaechtig als Auftragsfolge
gestartet.

## 5. Offene Punkte - in dieser Reihenfolge

1. **`BRIDGE-0092`-Luecke entscheiden** (§2 oben, von April zuerst zu klaeren - Optionen
   vorlegen, nicht selbst waehlen).
2. **Umsetzungsplan Drei-Schichten-Modell bestaetigen oder korrigieren** (§4 oben, neu - Schritte
   1-5, Reihenfolge und Traeger fuer den Symbol-Graph insbesondere).
3. **2a - Projekt-ID-Dropdown** (§1 oben, mit April bereits abgestimmter naechster Schritt).
4. **2b - Hamburger-Menue-Scope klaeren**, dann Auftrag ableiten.
5. **2c - `--machine`-Regel** in `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` nachtragen.
6. (unveraendert aus v16-v20: Quellen-Manifest `rag/sources.yaml` real anlegen, generische
   Steuerchat-Vorlage/Dorfschaft-Einbindung/Draft-Modus.)

## 6. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
(unveraendert aus v16-v19, zusaetzlich aus v20:) `machine: vm` in alten Audit-Eintraegen ist
erklaert und bewusst nicht korrigiert (append-only) - nicht erneut als Bug melden. Die
Drei-Schichten-Architektur selbst benoetigt **kein** neues Gate (BRIDGE-0096, Spezifikation §5) -
nicht erneut als offene Governance-Frage aufwerfen, nur die konkrete Umsetzungsreihenfolge (§4/§5
Punkt 2 oben) ist offen.

## 7. Referenz
v20 (`01beb76`) ist die unmittelbare Vorsitzung dieser Datei und bleibt die primaere Quelle fuer
BRIDGE-0093 bis -0100 im Detail - v21 fasst nur zusammen, ersetzt v20 nicht inhaltlich.
