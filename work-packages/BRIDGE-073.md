# BRIDGE-0073 - Abgleich "Steering Continuity"-Konzept gegen Gate/Handover/Entscheidungs-System

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0073 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Teile (alte Nummern) | keine (neuer Auftrag, kein Buendel) |
| Rechte | WORKTREE_WRITE, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / MEDIUM** - Konzeptvergleich mit Entscheidungscharakter, kein Widerspruchs-/Sicherheitsfall, daher nicht HIGH. |
| Modellwechsel zum Vorgaenger | JA (Vorgaenger BRIDGE-0072 war Claude Sonnet 5 / LOW, DOCS) |
| depends_on | BRIDGE-0072 (ARCHIVED) |
| Gate | keines (reine Konzeptpruefung, kein G2/G3/G4-Scope beruehrt) |
| stop_conditions | CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0073` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag

**Ziel:** Eine Entscheidungsdatei, die das extern vorgeschlagene "Steering Continuity"-Datenmodell (Program, WorkPackage, SteeringSession, Checkpoint, Decision, OpenIssue, Dependency, Collision, Baseline, HandoverState, ChangeRequest) Baustein fuer Baustein gegen den real vorhandenen Mechanismus stellt (Gates G0-G5, `docs/handover/ACB-UEBERGABE-v<N>.md`, `docs/concepts/ENTSCHEIDUNG-*.md`, `scripts/steuerchat-vorlage.py`, `docs/ACB-STEUERCHAT-STANDARDSTART.md`). Keine Implementierung, kein neues Schema.

**Scope:** Neu: `docs/concepts/ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md` (max. 80 Zeilen, Tabellenform). Sonst nichts. Kein Code, kein `schemas/`-Eintrag, keine Aenderung an bestehenden Handover-/Entscheidungs-Dateien.

1. Pro vorgeschlagenem Objekt (siehe oben) in einer Tabellenzeile festhalten: vorhandenes Gegenstueck im Repo (Datei-/Mechanismusbeleg), Deckungsgrad (vollstaendig / teilweise / keines), und eine von drei Optionen:
   - **A - formalisieren:** bestehender informeller Mechanismus wird in ein Schema unter `schemas/` ueberfuehrt (Aufwand grob T-Shirt-Groesse S/M/L, kein Zeitplan).
   - **B - unveraendert lassen:** informeller Mechanismus bleibt wie er ist, kein Schema noetig.
   - **C - verwerfen:** im Übergabepaket vorgeschlagenes Objekt hat kein reales Gegenstueck und wird nicht uebernommen, mit einem Satz Begruendung.
2. Fuer Objekte ohne jedes Gegenstueck (laut Bestandspruefung: Dependency, Collision, Baseline, ChangeRequest als formale Objekte) gesondert vermerken, ob ein erkennbarer Bedarf besteht oder ob sie reine Vorratsdefinition des Übergabepakets ohne aktuellen Anwendungsfall im Repo sind.
3. Den ID-Namensraum-Konflikt explizit festhalten: Planungs-IDs "ACB-ST-0xx" aus dem Übergabepaket werden nicht als eigener Nummernkreis uebernommen; jeder tatsaechliche Folgeauftrag laeuft als naechste freie `BRIDGE-00NN`.
4. **Generizitaets-Pruefung anhand Dorfschaft als Testfall, kein Adapter-Entwurf.** Dorfschaft liefert die einzige aktuell bekannte konkrete Anforderungsform; sie wird ausschliesslich benutzt, um zu pruefen, ob die generischen Objekte aus 04_DATENMODELL_STRUKTUR_GATES.md diese Form tragen KOENNTEN - nicht um sie fuer Dorfschaft festzulegen. Fuer jeden der folgenden sechs Punkte: Bewertung TRAEGT / TRAEGT NICHT / UNKLAR plus Fundstelle im bestehenden ACB-Mechanismus bzw. im Übergabepaket.
   - a) `Program.Phase` muss eine offene, adapterdefinierte Phasenfolge tragen koennen (Dorfschaft-Quelle nennt mindestens sechs bis acht Stufen: Landkarte, Einzelkonzepte, Einzelkonzept-Baseline, projektweiter Cross-Check, Kollisionsbereinigung, zweiter Cross-Check, Integrations-Gate) - kein in ACB fest verdrahteter Wertebereich.
   - b) `WorkPackage.Kapitelstatus` muss eine variable Anzahl Teilstatus abbilden koennen (Dorfschaft-Quelle: 27 Kapitel je Fachkonzept) mit einer vom Adapter definierten, nicht in ACB hartkodierten Statustaxonomie (Beispiel Dorfschaft: VOLLSTAENDIG VORHANDEN / TEILWEISE VORHANDEN / NUR VERTEILT DOKUMENTIERT / FEHLT).
   - c) Gatebericht in Checkpoint/HandoverState muss eine vom Adapter definierte, beliebig lange UND-Verknuepfung benannter Bedingungen abbilden koennen (Dorfschaft-Quelle: Integrations-Gate mit elf Matrix-/Register-Vollstaendigkeiten plus geloeste K1-K6-Konflikte plus Benutzerfreigabe) - nicht nur ACB-eigene technische Kriterien.
   - d) `Baseline` muss pro Einzelartefakt einfrierbar sein, nicht nur programmweit (Dorfschaft-Beispiel: FACHKONZEPT_INVESTITION V0.1 ENTWURF -> V0.2 KOLLISIONSBEREINIGT als eigene Revision, Vorgaengerversion bleibt gueltig).
   - e) `Collision.Profilklasse` muss eine adapterdefinierte Konflikttaxonomie tragen koennen (Dorfschaft-Quelle: K1-K6).
   - f) `SteeringSession` muss mehrere gleichzeitig laufende Sitzungen auf demselben `Program`/`WorkPackage` tragen koennen (parallele Fachdomaenen-Bearbeitung je Einzelkonzept) plus mindestens eine Sitzungsrolle, deren Aufgabe ausschliesslich die Kompatibilitaetspruefung aller Einzelarbeiten gegen das zentrale Ziel ist - als freie, adapterdefinierte Rollenbezeichnung im bestehenden `Rolle`-Feld, nicht als eigene ACB-Objektklasse "Integrationsagent". Hintergrund: April hat den fachlichen Bedarf an paralleler Mehrfachbearbeitung mit zentraler Kompatibilitaetspruefung fuer Dorfschaft-Fachkonzepte bereits bestaetigt (deckt sich mit Dorfschaft-Quelle §41/§54/§57f.) - das ist eine fachliche Festlegung fuer Dorfschaft, KEINE Freigabe fuer MULTI-AGENT-Ausfuehrung in ACB (siehe Punkt 5).
   Ausdruecklich NICHT Teil dieses Auftrags: Dorfschaft-Kapitelnamen, -Phasennamen, -Statuswerte, K1-K6 oder Dorfschaft-Agentenrollen selbst in ACB-Code, -Schema oder -Dokumentation uebernehmen. Sie dienen nur als Pruefmassstab.
5. Keine Aussage zu einem konkreten Dorfschaft-Adapter-Inhalt treffen - G5 bleibt unberuehrt und wird hier nicht neu bewertet. Codex-Rollenbeschraenkung in der Dorfschaft-Fachkonzeptphase (Analyse-/Review-Instrument, keine Fachfreigabe, laut Dorfschaft-Quelle §56) wird als bereits geltende inhaltliche Grenze vermerkt, nicht bewertet. Der fachliche Bedarf an Multi-Agent-Arbeit fuer Dorfschaft (§57f., durch April bestaetigt, siehe Punkt 4f) wird als "fachlich gesetzt" vermerkt - die davon getrennte Ausfuehrungsfreigabe fuer MULTI-AGENT-Betrieb in ACB (Schreibkonflikte, Writer-Lock/Ressourcenregel analog BRIDGE-0063, Freigabekette) bleibt ein eigener, noch offener, spaeterer ACB-Auftrag und wird hier weder entschieden noch vorbereitet - MULTI-AGENT bleibt in diesem Auftrag NEIN.
6. Status: FREIGEGEBEN durch April (02.10.2026). Freigabe umfasst den Auftragsumfang wie oben spezifiziert (Punkte 1-5), keine darueber hinausgehende Erweiterung ohne neue Freigabe.

**Tests:** Keine.

- [x] Entscheidungsdatei mit vollstaendiger Objekttabelle (11 Zeilen, siehe Punkt 1)
- [x] Sondervermerk zu Objekten ohne Gegenstueck (Punkt 2)
- [x] ID-Namensraum-Konflikt explizit dokumentiert (Punkt 3)
- [x] Generizitaets-Pruefung a-f mit TRAEGT/TRAEGT NICHT/UNKLAR je Punkt (Punkt 4), ohne Dorfschaft-Fachwerte oder -Agentenrollen in ACB zu uebernehmen
- [x] Vermerk zu Codex-Rollenbeschraenkung (geltend) und Multi-Agent-Ausfuehrungsfreigabe (fachlich gesetzt, Ausfuehrung weiterhin offen) als eigener spaeterer Auftrag (Punkt 5)
