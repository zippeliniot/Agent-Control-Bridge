# BRIDGE-0103: Qualitaetsrahmen fuer Steuerchat-Uebergaben spezifizieren

| Feld | Wert |
|---|---|
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** - T2 Konzeptarbeit: kein Code, aber eigene Abgrenzungsentscheidungen (welche Kriterien gehoeren hinein, welche nicht) innerhalb einer klaren Vorlage (Anmerkung + bestehende Dokumente als Grundlage). |
| Rechte | WORKTREE_WRITE, GIT_COMMIT, GIT_PUSH |
| Scope | `docs/concepts/QUALITAETSRAHMEN-STEUERCHAT-UEBERGABEN.md` (neu) |

## Anlass

Externe Pruefung (April, 10.10.2026) des Drei-Schichten-Umsetzungsplans empfahl als ersten
Schritt, Qualitaetskriterien fuer Steuerchat-Uebergaben eigenstaendig festzulegen, bevor
Decision-Log/Context-Assembler/Graph weiter spezifiziert werden (Begruendung: ohne einen
klaren Massstab besteht das Risiko, ein technisch funktionierendes, aber am eigentlichen
Uebergabe-Zweck vorbei entworfenes Datenmodell zu bauen). Der Steuerchat hat die Anmerkung
gegen den echten Repo-Stand verifiziert
(`docs/concepts/ENTSCHEIDUNG-DREISCHICHTEN-NAECHSTE-SCHRITTE.md` §3/§4/§5, Teil der
Uebergabe v24): Punkt E (dieser Auftrag) ist einer von zwei tatsaechlich neuen, wertvollen
Befunden der externen Pruefung und wurde auf Reihenfolgeposition 1 (E->F->B->A->C->D)
gesetzt, von April bestaetigt (10.10.2026).

**Wichtig fuer Claude Code:** Die Kriterien liegen heute bereits implizit, verteilt in
`docs/ACB-STEUERCHAT-STANDARDSTART.md` (Abschnitt 5) und
`docs/ACB-STEUERCHAT-ARBEITSWEISE.md` (Abschnitte 1 und 5) vor. Dieser Auftrag fasst sie
**explizit als eigenstaendiges, pruefbares Dokument** zusammen - er erfindet keine neuen
Regeln, sondern macht bestehende, bereits gelebte Praxis als Checkliste nutzbar (fuer
Menschen beim Lesen einer Uebergabe UND als Grundlage fuer eine kuenftige automatisierte
Pruefung, BRIDGE-0103 Folgeauftrag F in der bestaetigten Reihenfolge).

## Entscheidung zum Umfang (bewusste Abgrenzung)

Nur das Kriteriendokument selbst - **keine** Aenderung an `ACB-STEUERCHAT-STANDARDSTART.md`
oder `ACB-STEUERCHAT-ARBEITSWEISE.md` (die bleiben gueltig, dieses Dokument verweist auf sie,
ersetzt sie nicht), **keine** Code-/Schema-Aenderung, **keine** `wp-lint.py`-Erweiterung (das
ist der bereits separat bestaetigte Folgeauftrag "F", eigener BRIDGE-Auftrag).

## Ergebnisvertrag

Neues Dokument `docs/concepts/QUALITAETSRAHMEN-STEUERCHAT-UEBERGABEN.md` mit mindestens:

1. **Pflichtbestandteile einer gueltigen Uebergabe** (aus der externen Pruefung, woertlich
   uebernommen als Mindestanforderung): bestaetigter Projektstand, Quelle und Zeitstand
   wichtiger Aussagen, Entscheidungen samt Geltungsbereich, offene und erledigte Auftraege,
   Blockaden, der naechste zulaessige Schritt.
2. **Pflicht zur sichtbaren Ungeklaertheit**: unbelegte oder widerspruechliche Angaben
   muessen explizit als ungeklaert markiert erscheinen, nicht stillschweigend geglaettet
   werden (Kernlehre aus dem in dieser Sitzung behandelten Kernbefund: eine Anmerkung, die
   einen ueberholten Zwischenstand bewertet, waere mit dieser Regel schneller als veraltet
   erkennbar gewesen).
3. **Abgrenzung zu bestehenden Dokumenten**: explizite Tabelle, welches bestehende Dokument
   (`STANDARDSTART.md`, `ARBEITSWEISE.md`) welchen Teil der Kriterien bereits (teilweise)
   abdeckt - dieses Dokument fasst zusammen, ersetzt nicht.
4. **Pruefbarkeitskriterium je Punkt**: zu jedem Pflichtbestandteil (Punkt 1) eine
   kurze, konkrete Frage, mit der ein Mensch oder ein kuenftiges Skript (Folgeauftrag F)
   prüfen kann, ob eine vorliegende Uebergabedatei den Punkt erfuellt oder nicht.

## Akzeptanzkriterien

- [x] Dokument enthaelt alle sechs in der externen Pruefung genannten Pflichtbestandteile,
  nicht nur eine Teilmenge
- [x] Regel zur sichtbaren Ungeklaertheit ist enthalten und mit einem konkreten Beispiel aus
  dem Repo belegt (z. B. der v24-Kernbefund)
- [x] Abgrenzungstabelle zu `STANDARDSTART.md`/`ARBEITSWEISE.md` vorhanden, keine
  Dopplung/kein Widerspruch zu deren bestehendem Inhalt
- [x] Jeder Pflichtbestandteil hat eine Pruefbarkeitsfrage
- [x] Kein Code, kein Schema, keine Aenderung an anderen Dateien als dem neuen Dokument
- [ ] Volle Suite bleibt gruen (reine Doku-Aenderung, keine Regression zu erwarten, trotzdem
  einmal am Ende laufen lassen und Zahl nennen)
