# ACB-Leseanweisung Steuerchat-Start (Fehlerbefund + Pflichtzusatz)

## §1 Fehlerbefund aus dem letzten Übergang

Im laufenden Übergang trat folgender Fehler auf: Der erste an Claude Code
ausgelieferte Auftragsblock (BRIDGE-0103) enthielt nicht die Pflichtzeile
`MODELL: <Modell> / DENKSTUFE: <Stufe>`, obwohl diese in mehreren
Primärquellen ausdrücklich verlangt ist (`docs/architecture/ARCHITECTURE.md`
§13, `docs/PROJEKTKONZEPT.md` §27/§34: „Modell und Denkstufe werden vor jedem
Arbeitsblock ausdrücklich genannt"). April musste den Fehler händisch
korrigieren lassen.

Ursache: Diese Anforderung stand in Dokumenten, die als „bei Bedarf"
eingestuft und deshalb beim Session-Start nicht vollständig bis zum Ende
gelesen wurden, sondern nur selektiv/überfliegend. Das Muster ist identisch
mit dem ursprünglich benannten Problem ("alle start fehler verhindert werden
die duch nur teileweises lesen der gesamten dokument entstanden ist") — es
ist trotz expliziter Anweisung am Sitzungsanfang erneut aufgetreten, weil
„bei Bedarf" faktisch als „überspringen" ausgelegt wurde.

## §2 Verbindliche Leseanweisung (ab sofort, für jeden Steuerchat-Start)

1. Kein Dokument der Pflichtlese-Liste gilt als gelesen, wenn es nicht
   vollständig bis zur letzten Zeile gelesen wurde — auch nicht, wenn der
   gesuchte Inhalt scheinbar schon früher im Dokument gefunden wurde.
   Abbrechen nach dem ersten relevanten Treffer ist nicht vollständiges
   Lesen.
2. „Bei Bedarf" bedeutet nicht „optional/überspringbar", sondern:
   spätestens lesen, sobald der erste Auftrag vorbereitet wird, der von
   diesem Dokument betroffen sein könnte (z. B. jeder Auftrag an Claude
   Code → vorher `ARCHITECTURE.md` und `PROJEKTKONZEPT.md` vollständig
   lesen, nicht nur `STANDARDSTART.md`).
3. Verstehen bestätigen, nicht nur Lesen bestätigen. Nach dem vollständigen
   Lesen muss erkennbar sein, dass die Pflichtfelder/-formate aus dem
   Dokument tatsächlich in die eigene Ausgabe übernommen wurden (Stichprobe:
   enthält der erste produzierte Auftragsblock alle dort verlangten
   Pflichtzeilen?).
4. Bei Zweifel, ob ein Dokument vollständig gelesen wurde: erneut lesen,
   nicht aus dem Gedächtnis rekonstruieren.

## §3 Zusatz für den Startprompt (in STANDARDSTART.md einzufügen)

Dringend vor dem ersten Auftrag: Alle unter „Primärquellen" und „bei
Bedarf" gelisteten Dokumente vollständig bis zum Ende lesen — nicht nur
bis zur ersten vermeintlich relevanten Stelle. Nach dem Lesen aktiv
prüfen, ob alle dort verlangten Pflichtformate (insbesondere
MODELL/DENKSTUFE-Zeile, Pflicht-Footer, Berechtigungsprofil-Vollständigkeit)
im eigenen ersten Auftragsblock tatsächlich vorkommen. Lesen ohne Umsetzung
in der eigenen Ausgabe zählt nicht als erledigt.

## §4 Einordnung

Dieses Dokument ersetzt nichts Bestehendes, sondern ergänzt
`docs/ACB-STEUERCHAT-STANDARDSTART.md` um einen expliziten Fehlerbefund +
Pflichtzusatz.
