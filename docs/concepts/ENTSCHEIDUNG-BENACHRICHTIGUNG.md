# Entscheidung: Windows-Benachrichtigung bei Fertigmeldung (BRIDGE-0068)

**Status: FREIGEGEBEN (2026-09-21, Option A, nur Fertigmeldung).** Keine Implementierung in diesem Auftrag.

## 1. Ist-Stand
Der Executor pusht `result.yaml`, der Auftrag steht auf `WAITING_FOR_COPY_TO_CONTROL`.
Der Board-Klon holt den Stand per Auto-Pull (`webui serve`, Standard 30 s). April bemerkt die
Fertigmeldung nur durch Hinsehen in Web-UI bzw. Board.

## 2. Funktion
Windows-Benachrichtigung auf der Maschine mit der Web-UI, sobald ein Auftrag **neu** auf
`WAITING_FOR_COPY_TO_CONTROL` steht. Inhalt nur Auftrags-ID und Titel, kein Ergebnisinhalt.

## 3. Optionen fuer den Ort
- **(A) Hook im Auto-Pull-Thread von `webui serve`.** Laeuft heute periodisch nach jedem Pull; es fehlt
  ein Vorher/Nachher-Abgleich der Status und der Notifier-Aufruf. Grenze: nur solange der Server laeuft.
- **(B) `board --watch`.** Laeuft heute als Terminal-Schleife mit Neuanzeige; es fehlt derselbe Abgleich
  und der Notifier, zudem ein eigener Pull. Grenze: nur solange das Terminal-Fenster offen ist.

## 4. Kanal
Windows-Toast ueber `powershell.exe` (Bordmittel, keine Zusatzpakete), kein Netz, keine Mail.
Aktivierung nur per Opt-in-Flag (z. B. `--notify`); ohne Flag unveraendertes Verhalten.
Nicht-Windows: still, ohne Meldung und ohne Fehler.

## 5. Regeln
- **Rein lesend:** kein Store-Write, kein Statuswechsel, kein Audit-Eintrag; Gate G2 unberuehrt.
- **Fail-open:** Fehler der Meldung (PowerShell fehlt, Timeout, Exit-Code) wird hoechstens geloggt
  und bricht weder Pull noch Server ab.
- **Entprellung:** je Zustandseintritt genau eine Meldung. Beim Start wird der aktuelle Bestand als
  Basis gemerkt, Altbestand wird nicht gemeldet. Verlassen und Wiedereintritt meldet erneut.
- **Injizierbarer Notifier:** Erkennung und Ausgabe getrennt; Tests laufen unter Linux mit Fake-Notifier.

## 6. Empfehlung
**Option A.** Die Web-UI ist Aprils Arbeitsflaeche, der Auto-Pull-Thread kennt den Zeitpunkt neuer
Daten bereits; B braeuchte ein zusaetzliches Fenster und eine zweite Pull-Logik.

**Schnitt BRIDGE-0069 (T2, Sonnet 5 / MEDIUM):** Reine Funktion "neu eingetretene
WAITING_FOR_COPY_TO_CONTROL-Auftraege" (Basis/Aktuell) + Notifier-Schnittstelle mit PowerShell-Toast und
Null-Notifier; Einhaengen in den Auto-Pull-Thread hinter `--notify`; Tests fuer Entprellung, Neustart, fail-open.
