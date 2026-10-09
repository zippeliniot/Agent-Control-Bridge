# ACB - Uebergabe v22 (Stand 2026-10-09)

**Repo-HEAD bei Erstellung:** `5bdd8447c33736f1d03328d757e2200de9bbcd6a` (`5bdd844`) | **Tests:**
594/594 - zuletzt in dieser Reihe unabhaengig frisch nachgelaufen vor BRIDGE-0100/v20; seither
keine Code-Aenderung, nur Dokumentation (v20, v21) und die in Abschnitt 1 beschriebenen
Store-Aenderungen (neues OpenIssue, Audit-Merge).

**Fuer den neuen Steuerchat:** `docs/ACB-STEUERCHAT-STANDARDSTART.md`, diese Datei. v19, v20 **und**
v21 nicht loeschen (Historie).

**Anlass dieser Version:** Beim Staging von v21 durch April selbst (PowerShell, Maschine mit
lokal ungepushtem Vorlauf) traten zwei reale, bisher unbekannte Befunde auf, die v21 noch nicht
enthielt. v22 dokumentiert beide, zusaetzlich zur vollstaendigen Uebernahme von v21.

## 1. Neu in dieser Version: zwei Befunde aus dem Staging-Vorgang

### 1a. `ISSUE-0005` real angelegt, OPEN (neu, nicht Teil von v20/v21)

Beim Versuch, v21 zu pushen, zeigte sich ein lokal divergierter Branch (1 ungepushter Commit).
Dieser Commit legte ein neues `OpenIssue` an - urspruenglich faelschlich als `ISSUE-0004`
nummeriert (Kollision mit dem bereits existierenden, laengst `CLOSED` `ISSUE-0004` zur
Testzahl-Diskrepanz 576/575), da die lokale CLI die naechste freie ID anhand eines veralteten
lokalen Standes berechnet hatte (47 Commits hinter `origin/main`). Korrigiert (Umbenennung +
Audit-Eintrag angepasst, noch vor dem ersten Push, daher keine Store-Faelschung) und unter der
echten naechsten freien ID gepusht:

```
open-issues/agent-control-bridge/agent-control-bridge-ISSUE-0005.yaml
status: OPEN
summary: push_mode steht bei keinem der sieben Projekte auf draft (M1 Single-Writer nicht aktiv);
  der gemeinsame ACB-Store-Branch (main) erlaubt dadurch Commit-Races zwischen gleichzeitig
  laufenden Steuerchats verschiedener Projekte - git selbst verhindert Datenverlust (kein
  Force-Push), aber changed_files/base_head in result.yaml werden unprojiziert ueber das ganze
  Repo berechnet und ziehen fremde Projekt-Commits mit rein (real beobachtet bei BRIDGE-0091,
  Wetter-Steuerchat-Commits a2600a4/22b4233)
origin_task_id: BRIDGE-0091
```

**Status: OPEN, nicht geschlossen.** Fuer den neuen Steuerchat: dieses Issue ist ein echter,
ungeloester Befund (keine Projekt-/Task-Ebene erzwingt aktuell `push_mode: draft`, M1
Single-Writer ist nirgends aktiv) - nicht mit den bereits `CLOSED` Issues 0001-0004 verwechseln.
Erfordert eine Entscheidung: entweder mindestens ein Projekt/Task auf `push_mode: draft`
umstellen (betrifft `docs/concepts/ENTSCHEIDUNG-PUSH-MODELL.md`), oder `changed_files`/`base_head`
in `result.yaml` projektbezogen statt repo-weit berechnen (Code-Aenderung), oder beides. Keine
der beiden Optionen ist hier bereits gewaehlt.

### 1b. `audit/audit.jsonl` enthaelt bereits seit laengerem zwei ungueltige, literale
Git-Konfliktmarker-Zeilen (neu entdeckt, nicht durch diese Sitzung verursacht)

Beim Zusammenfuehren des o.g. lokalen Commits mit `origin/main` zeigte sich beim Pruefen des
Merge-Konflikts in `audit/audit.jsonl`, dass **unabhaengig vom aktuellen Merge** bereits zwei
Zeilen mit literalem, nie aufgeloestem Git-Konfliktmarker-Text in der realen, bereits gepushten
Historie stehen - verifiziert durch direktes Pruefen von `origin/main:audit/audit.jsonl` **vor**
jeder eigenen Aenderung dieser Sitzung:

```
Zeile 824: <<<<<<< HEAD
Zeile 839: >>>>>>> eb214ad7f778bc3b597f7b2656c312fd3dbde206
```

(`eb214ad` = realer Commit "Ops: BRIDGE-0093 task_archive" - der Fehler stammt aus einer frueheren
Sitzung, die einen eigenen Merge-Konflikt zwischen WETTER-0016- und BRIDGE-0093-Aenderungen nicht
richtig aufgeloest und die Marker versehentlich mitcommittet hat, vermutlich um den
10.10.2026 11:09-11:15 Uhr herum, siehe Zeitstempel der umgebenden Zeilen.) Diese zwei Zeilen
sind **kein gueltiges JSON** - jedes Tool, das `audit.jsonl` zeilenweise als JSON parst
(`json.loads` pro Zeile), bricht an genau diesen zwei Stellen ab oder muesste sie uebergehen.

**Nicht in dieser Sitzung korrigiert:** append-only, bereits real gepusht - eine rueckwirkende
Bereinigung waere eine Aenderung an bereits committeter, geteilter Historie und faellt unter die
gleiche Regel wie die BRIDGE-0092-Luecke (nicht eigenmaechtig entscheiden). Drei moegliche Wege,
analog zu v21 Abschnitt 2, keiner gewaehlt:
1. Nichts tun, nur als bekannter historischer Defekt dokumentieren (jedes parsierende Tool muss
   das selbst robust behandeln).
2. Einen neuen, einmaligen "Korrektur-Commit" anlegen, der ausschliesslich diese zwei Zeilen
   entfernt (aendert erstmals bewusst eine historische Zeile - Praezedenzfrage wie bei
   BRIDGE-0092 Option 1).
3. Als eigenes `OpenIssue` dokumentieren (analog zu den bisherigen funf) und offen lassen, bis
   ein Tool tatsaechlich daran scheitert.

## 2. Aus v21 vollstaendig uebernommen

### 2a. Aus v20 (real gepusht)

BRIDGE-0093 bis BRIDGE-0100 `ARCHIVED`, gepusht, Details v20 §1. Drei offene Punkte,
**unveraendert, nicht umgesetzt**:
- **2a.** Projekt-ID-Dropdown statt Freitext (mit April abgestimmt, noch nicht umgesetzt).
- **2b.** Hamburger-Menue-Scope ungeklaert.
- **2c.** `machine: vm` in Audit-Eintraegen - erklaert, kein Bug, `--machine`-Regel noch nicht in
  `ACB-STEUERCHAT-ARBEITSWEISE.md` nachgetragen.

### 2b. `BRIDGE-0092`-Luecke (aus diesem Chat, in v20 nicht dokumentiert)

`BRIDGE-0092` wird in drei Stellen als abgeschlossener Auftrag zitiert, existiert aber nicht als
`tasks/BRIDGE-0092/` oder `work-packages/BRIDGE-092.md` (Commit `7fa95f9` lief ohne Auftrags-
Zyklus). Drei Optionen in v21 §2, keine gewaehlt - **April vorlegen, nicht selbst waehlen.**

### 2c. Drei-Schichten-Modell: Status und Umsetzungsplan

Nicht als ausfuehrbarer Auftrag abgebildet, nur Entscheidungsentwurf
(`ENTSCHEIDUNG-DREI-SCHICHTEN-STEERING-CONTINUITY.md`, Status ENTWURF) und Spezifikation
(BRIDGE-0094). Fuenf reale Vorbereitungsauftraege (0093/0094/0096/0097/0098), aber kein
Indexer-/Assembler-/Decision-Log-CLI-Code. April: Vektor-RAG allein ist nicht funktionsfaehig als
verlaessliche Quelle fuer die Steuerchat-Uebergabe - erst in Kombination mit Decision-Log und
Symbol-/Datei-Graph erreicht die Uebergabe das angestrebte hohe Qualitaetsniveau (Beleg:
Spezifikation §1 - RAG-Treffer bleiben "ungeprueftes Hintergrundmaterial" ohne die beiden
strukturierten Schichten). Umsetzungsplan (Vorschlag, von April zu bestaetigen):
1. Decision-Log-CLI-/Store-Anbindung fuer `schemas/decision.schema.yaml`.
2. Symbol-/Datei-Graph: Traegerfrage klaeren (wer baut/pflegt), dann Indexer beauftragen
   (Tree-sitter-Spike BRIDGE-0098 bereits abgeschlossen, kein Blocker).
3. Context-Assembler-Schema entwerfen (bisher nur Sketch).
4. Routing-Feld entscheiden (welches Schema-Feld steuert die Schicht-Auswahl).
5. Erst danach ist das Vektor-RAG-Archiv als vollwertiger, eingeordneter Fallback nutzbar.

## 3. G-Status
Unveraendert zu v16-v21 (G0-G5, G6 weiterhin nicht konzipiert).

## 4. Offene Punkte - in dieser Reihenfolge

1. **`ISSUE-0005` (neu, §1a):** push_mode/Commit-Race-Entscheidung - mindestens ein Projekt auf
   `draft` umstellen und/oder `changed_files`/`base_head`-Berechnung projektbezogen machen.
2. **Alte Konfliktmarker in `audit.jsonl` (neu, §1b):** drei Optionen vorlegen, nicht selbst
   waehlen.
3. **`BRIDGE-0092`-Luecke entscheiden** (§2b).
4. **Umsetzungsplan Drei-Schichten-Modell bestaetigen oder korrigieren** (§2c).
5. **2a - Projekt-ID-Dropdown** (mit April bereits abgestimmter naechster Schritt).
6. **2b - Hamburger-Menue-Scope klaeren**, dann Auftrag ableiten.
7. **2c - `--machine`-Regel** in `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` nachtragen.
8. (unveraendert aus v16-v21: Quellen-Manifest `rag/sources.yaml`, generische
   Steuerchat-Vorlage/Dorfschaft-Einbindung/Draft-Modus.)

**Naechste freie BRIDGE-ID: BRIDGE-0101** (unveraendert). **Naechste freie Issue-ID: `ISSUE-0006`**
(neu zu pruefen: vor jeder Neuvergabe zuerst `bridge issue list --include-closed` gegen den
frischen `origin/main`-Stand laufen lassen - genau das fehlte beim `ISSUE-0005`-Vorfall, §1a).

## 5. Nicht von selbst anfangen bei (geklaert, nicht erneut hinterfragen)
(unveraendert aus v16-v21:) `machine: vm` in alten Audit-Eintraegen ist erklaert, bewusst nicht
korrigiert. Kein neues Gate fuer die Drei-Schichten-Architektur (BRIDGE-0096, entschieden) - nur
die Umsetzungsreihenfolge (§2c/§4 Punkt 4) ist offen.

## 6. Referenz
v20 und v21 bleiben Primaerquellen im Detail (BRIDGE-0093 bis -0100 bzw. Drei-Schichten-Bewertung)
- v22 fasst zusammen und ergaenzt nur die zwei neuen Befunde aus dem Staging-Vorgang, ersetzt
weder v20 noch v21 inhaltlich.
