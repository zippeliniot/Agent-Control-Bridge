# Entscheidung: Audit-Strategie (Dateiaufteilung)

**Status:** FREIGEGEBEN (2026-09-20, Option A). BRIDGE-0059, Gate G2.

## 1. Ist-Stand
- `audit/audit.jsonl`: eine Datei, JSON Lines, Append-only.
- Stand WP-Erstellung: ca. 260 Zeilen / ca. 58 KB.
- Messung 20.09.2026: 373 Zeilen / 83.451 Byte. Wachstum: +113 Zeilen seit gestern (intensive Umsetzungsphase), Dauerwert offen.

## 2. Optionen
**A - Eine Datei + sicheres Append (Empfehlung).** Alles bleibt in
`audit/audit.jsonl`; Append zeilenweise geschrieben und geflusht, damit keine
halbe Zeile entsteht.

**B - Monatsdateien.** `audit/audit-YYYY-MM.jsonl`; Schreiber waehlt nach
Ereigniszeit, Leser fuehrt mehrere Dateien in Zeitreihenfolge zusammen.

**Schwellwert A -> B:** erst ab **1 MB** oder **5000 Zeilen**. Beide Werte sind
derzeit um mehr als Faktor 10 entfernt, B ist verfrueht.

## 3. Konsequenz fuer den Lesecode
**`last_transition_at`**
- A: unveraendert - eine Datei rueckwaerts lesen, erster Treffer gewinnt.
- B: Monatsdateien absteigend durchgehen, bis ein Treffer faellt.

**overview**
- A: unveraendert - ein Durchlauf ueber eine Datei.
- B: Verkettung/Sortierung aller Monatsdateien vor der Auswertung noetig.

**watcher**
- A: unveraendert - ein Dateihandle, Offset bleibt gueltig.
- B: muss den Monatswechsel erkennen und auf die neue Datei umschalten.

## 4. Empfehlung
Option **A** beibehalten. B erst bei erreichtem Schwellwert aus §2, dann als
eigenes Arbeitspaket samt Migration des Lesecodes.
