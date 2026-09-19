# Entscheidung: Push-Modell und Kollisionsschutz-Grundlage

Status: FREIGEGEBEN
Auftrag: BRIDGE-0043 | Gate: G1 | Grundlage: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3 R7, §5 G2, §6 Punkte 2,3

## Problem
V1 und CLAUDE.md erlauben dem Executor `git push` und Schreibzugriff auf den Store;
Stufe A des V2-Konzepts verlangt einen Single Writer. Beides gleichzeitig ist nicht haltbar.

## Optionen

### A - Alles bleibt: Executor pusht
- Folge: keine Aenderung an CLAUDE.md, Sofort-Push-Pflicht und `GIT_PUSH` gelten weiter.
- Folge: Stufe A (BRIDGE-0049..0055) waere ohne Wirkung, G2 nicht erreichbar.
- Risiko: zwei Maschinen schreiben parallel auf `tasks/`, `results/`, `audit/` - Lost Update, kaputte Historie.

### B - Draft-Modus nur pro Projekt per Feld `push_mode` (EMPFEHLUNG)
- Folge: `push_mode: direct` (Default) behaelt heutiges Verhalten; `push_mode: draft` schaltet ein Projekt auf Executor-Draft + Board-Import um.
- Folge: Umstellung projektweise und rueckrollbar; ACB kann vor Dorfschaft umgestellt werden.
- Risiko: zwei Pfade gleichzeitig pflegen; das Feld muss tatsaechlich ausgewertet werden, sonst falsche Sicherheit.

### C - Sofort Single-Writer
- Folge: Executor-Push und Executor-Write unter `tasks/`, `results/`, `audit/` sofort gesperrt.
- Folge: Alle laufenden Auftraege brauchen ab sofort den Board-Import, der noch nicht existiert.
- Risiko: Arbeit blockiert, bis BRIDGE-0049..0054 fertig sind - Stillstand ohne Rueckfallebene.

## Empfehlung
**Option B.** Sie loest den Widerspruch, ohne den laufenden Betrieb anzuhalten, und macht die
Umstellung pro Projekt messbar. Das Feld `push_mode` wird in BRIDGE-0047 eingefuehrt.

## Uebergangsregel bis Gate G2
- Bis G2 `IN KRAFT` gilt CLAUDE.md unveraendert: Auftraege mit `GIT_PUSH` duerfen pushen,
  jeder Teilschritt-Commit wird sofort gepusht.
- G2 tritt erst in Kraft nach PASS von BRIDGE-0055 und ausdruecklichem Eintrag durch April.
- Ab G2 gilt der Draft-Modus nur in Projekten mit `push_mode: draft`: dort kein Executor-Push
  und kein Executor-Write unter `tasks/`, `results/`, `audit/`.
- Projekte ohne dieses Feld bleiben auf `direct` - kein stiller Wechsel.
- `--force`-Push bleibt in jedem Modus verboten.

## Kollisionsschutz V2 - Mindestspezifikation
Ein Kollisionsschutz-Dokument existiert im Repo nicht (Befund BRIDGE-0042, §6 Punkt 3).
Bis ein eigenes Konzept vorliegt, gilt diese Mindestspezifikation als verbindlich:

- **M1 Single Writer:** Pro Store (`tasks/`, `results/`, `audit/`) schreibt genau eine Instanz -
  das Board. Executoren liefern Drafts, sie mutieren den Store nicht.
- **M2 Writer-Lock:** Jeder Store-Write laeuft unter einem Lock (Lock-Datei mit PID, Host,
  Zeitstempel, TTL). Lock nicht erhaltbar = Abbruch mit Fehlercode, nach kurzem Timeout (max. 10 s), kein Endlos-Retry.
- **M3 Atomarer Write:** Schreiben in temporaere Datei im Zielverzeichnis, dann `os.replace`.
  Audit nur als Append unter demselben Lock. Keine Teilzustaende auf Platte.
- **M4 Abgelaufener Lock:** Nach TTL-Ablauf wird der Lock gemeldet, NICHT automatisch gebrochen; Uebernahme nur explizit durch den Bediener, das Ereignis
  wird im Audit vermerkt. Stille Uebernahme ist unzulaessig.
- **M5 CAS-Ausblick (Stufe B, Gate G3):** `task_version` je Auftrag; Schreiben nur bei
  passender Version, sonst Konflikt. Claim/Lease ergaenzt das fuer Parallelbetrieb.
  Umsetzung erst nach ausdruecklicher Freigabe (BRIDGE-0061/0062).

## Offen
Freigabe durch April: Status dieser Datei auf `FREIGEGEBEN` setzen. Ohne Freigabe bleibt G1 geschlossen.

Nummern: Teilpakete 0048,0050 -> 0047; 0051,0052 -> 0049; 0054 -> 0053; 0056 -> 0055; 0058 -> 0060; 0062 -> 0061; 0064 -> 0063 (siehe Konzept §2).
