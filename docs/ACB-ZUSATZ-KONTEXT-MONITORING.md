## Neue Pflichtregel: Kontext-Monitoring (für `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` einzufügen)

### Kontext-Monitoring-Pflicht

- Der Steuerchat beobachtet **laufend** seinen eigenen Kontextfüllstand.
- **Meldepflicht:** Sobald der Kontext spürbar voll wird (nicht erst wenn er
  faktisch voll ist), meldet der Steuerchat das aktiv und unaufgefordert an
  April — nicht erst auf Nachfrage.
- **Rechtzeitig Übergabe-Chat erstellen:** Bei dieser Meldung erstellt der
  Steuerchat direkt die nächste Übergabe (`docs/handover/ACB-UEBERGABE-vNN.md`)
  mit dem aktuellen Zwischenstand, statt zu warten, bis der Kontext tatsächlich
  voll ist und Informationen verloren gehen oder der nächste Chat bei null
  anfangen müsste.
- Ziel: kein abrupter Abbruch ohne Übergabe, kein nachträgliches Verifizieren
  unvollständiger Information durch den Folgechat.
