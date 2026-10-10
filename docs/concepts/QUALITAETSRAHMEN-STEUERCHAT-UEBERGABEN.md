# QUALITAETSRAHMEN: Steuerchat-Uebergaben

**Status: Spezifikation (BRIDGE-0103).** Kein Code, kein Schema. Dieses Dokument erfindet
keine neuen Regeln: Es fasst die heute verteilt und implizit gelebte Praxis
(`docs/ACB-STEUERCHAT-STANDARDSTART.md`, `docs/ACB-STEUERCHAT-ARBEITSWEISE.md`) als
eigenstaendige, pruefbare Checkliste zusammen. Es **ergaenzt** diese Dokumente und ersetzt sie
nicht.

Herkunft: externe Pruefung des Drei-Schichten-Umsetzungsplans (10.10.2026), bewertet in
`docs/concepts/ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md` §3 Punkt 1. Zweck: ein klarer
Massstab, woran eine Uebergabe gemessen wird, bevor Decision-Log, Context-Assembler oder Graph
weiter spezifiziert werden.

Geltungsbereich: jede Uebergabedatei, mit der ein neuer Steuerchat den Stand uebernimmt.
Eine Uebergabe ist **Momentaufnahme, kein Live-Zustand** (ARBEITSWEISE §5 Punkt 7).

## 1. Pflichtbestandteile einer gueltigen Uebergabe

Mindestanforderung, woertlich aus der externen Pruefung uebernommen. Fehlt einer der sechs
Bestandteile, ist die Uebergabe unvollstaendig.

| # | Pflichtbestandteil | Pruefbarkeitsfrage (Mensch oder kuenftiges Skript, Folgeauftrag F) |
|---|---|---|
| P1 | **Bestaetigter Projektstand** | Nennt die Uebergabe den Repo-Stand als konkreten `HEAD`-SHA **und** ist er als gegen einen frischen Klon bestaetigt gekennzeichnet (nicht nur uebernommen)? |
| P2 | **Quelle und Zeitstand wichtiger Aussagen** | Traegt jede wesentliche Aussage (Zahl, Status, Auftrags-ID, Dateiinhalt) eine pruefbare Quelle (Datei/Abschnitt/Commit) und ein Datum bzw. einen Stand-SHA? |
| P3 | **Entscheidungen samt Geltungsbereich** | Hat jede genannte Entscheidung einen Entscheider/Datum **und** einen Geltungsbereich (wofuer gilt sie, wofuer ausdruecklich nicht, ist sie endgueltig oder Entwurf)? |
| P4 | **Offene und erledigte Auftraege** | Sind offene und erledigte Auftraege getrennt aufgelistet, jeweils mit `BRIDGE-xxxx`-ID und Status, und stimmen die IDs mit `tasks/` und `work-packages/` im Klon ueberein? |
| P5 | **Blockaden** | Sind alle bekannten Blockaden (offene Issues, ausstehende Entscheidungen, fehlende Rechte) einzeln benannt — oder steht ausdruecklich „keine Blockaden"? |
| P6 | **Der naechste zulaessige Schritt** | Ist genau ein naechster Schritt benannt, der mit den Regeln aus `CLAUDE.md`/Sicherheitsmodell vereinbar ist, samt Verweis auf Freigabe, falls eine noetig ist? |

## 2. Pflicht zur sichtbaren Ungeklaertheit

**Regel:** Unbelegte, nicht nachpruefbare oder widerspruechliche Angaben muessen in der
Uebergabe **explizit als ungeklaert markiert** erscheinen (z. B. Abschnitt „Ungeklaert" oder
Kennzeichnung `UNGEKLAERT:` direkt an der Aussage). Sie duerfen weder weggelassen noch
stillschweigend geglaettet, harmonisiert oder „plausibel ergaenzt" werden. Das entspricht der
bestehenden Regel „Keine Dichtungen" (STANDARDSTART/ARBEITSWEISE §1) und macht sie in der
Uebergabe selbst sichtbar.

Pruefbarkeitsfrage: Gibt es zu jeder Aussage, die laut P2 keine Quelle hat oder einer anderen
Aussage widerspricht, eine ausdrueckliche Ungeklaert-Markierung — und enthaelt die Uebergabe
sonst keine solchen Aussagen unmarkiert?

**Beleg aus dem Repo (v24-Kernbefund):** Die externe Pruefung bewertete einen ueberholten
Zwischenstand (v22 §2c / v23 §5), dem die Primaerquellen `BRIDGE-0093`–`0100` nicht vorlagen
(`ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md` §2). Haette die zugrunde liegende
Zusammenfassung ihre Luecke („Stand der Schritte 1–5 nicht gegen Primaerquellen geprueft")
sichtbar als ungeklaert markiert, waere die Anmerkung schneller als veraltet erkennbar gewesen.
Zweiter Beleg: Am 09.10.2026 behauptete ein Konzeptdokument (Stand-Vermerk HEAD `b70ed66`)
faelschlich, `open-issues/` existiere nicht; drei von vier daraus angelegten Issues existierten
bereits (ARBEITSWEISE §5 Punkt 7).

## 3. Abgrenzung zu bestehenden Dokumenten

Dieses Dokument fasst zusammen, ersetzt nicht. Bei Widerspruch gelten die bestehenden
Dokumente; der Widerspruch ist als Befund zu melden.

| Kriterium | Bereits (teilweise) abgedeckt in | Was dieses Dokument zusaetzlich leistet |
|---|---|---|
| P1 Projektstand | STANDARDSTART §1, §5; ARBEITSWEISE §1 Punkte 1–2 (frischer Klon, HEAD-Abgleich, Abweichung zuerst melden) | Macht „gegen frischen Klon bestaetigt" zur pruefbaren Eigenschaft der Uebergabedatei |
| P2 Quelle/Zeitstand | ARBEITSWEISE §5 Punkte 1, 7 (Aussagen nicht ungeprueft glauben, Dokumente sind Momentaufnahmen) | Fordert Quelle und Stand **in** der Uebergabe, nicht nur bei der Pruefung |
| P3 Entscheidungen + Geltungsbereich | nur implizit (Uebergabeabschnitt 0 „bindende Regeln", ARBEITSWEISE §3) | Geltungsbereich als eigene Pflichtangabe |
| P4 Auftraege | ARBEITSWEISE §1 Punkt 6 (IDs selbst aus `tasks/`/`work-packages/` ermitteln) | Verlangt getrennte Liste offen/erledigt in der Uebergabe, abgleichbar mit §1 Punkt 6 |
| P5 Blockaden | ARBEITSWEISE §2 (ein Auftrag zur Zeit), §5 Punkt 6 (Push-Faehigkeit nicht annehmen) | Blockaden als eigener, nie leerer Abschnitt |
| P6 Naechster Schritt | STANDARDSTART §5 (mit offenen naechsten Schritten fortfahren) | Genau ein zulaessiger Schritt, regelkonform und mit Freigabehinweis |
| Ungeklaertheit (§2) | „Keine Dichtungen" (ARBEITSWEISE §1), STANDARDSTART §5 (Abweichungen explizit benennen) | Dieselbe Haltung, aber als Pflicht an die **Uebergabedatei** selbst |

## 4. Nicht Teil dieses Dokuments

- Keine Aenderung an `ACB-STEUERCHAT-STANDARDSTART.md` oder `ACB-STEUERCHAT-ARBEITSWEISE.md`.
- Keine Code-/Schema-Aenderung, keine `wp-lint.py`-Erweiterung (separater Folgeauftrag F in der
  bestaetigten Reihenfolge E→F→B→A→C→D).
- Keine Aussage ueber Datenmodell von Decision-Log, Context-Assembler oder Graph.
