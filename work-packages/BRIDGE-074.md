# BRIDGE-0074 - Formalisierungsentscheidung OpenIssue (Grundlage token-sparsame Steuerchat-Uebergabe)

| Feld | Wert |
|---|---|
| bridge_task_id | BRIDGE-0074 |
| project_id | agent-control-bridge |
| Typ / Klasse | T1 / ARCHITECTURE |
| Teile (alte Nummern) | keine (neuer Auftrag, kein Buendel) |
| Rechte | WORKTREE_WRITE, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Opus 5 / MEDIUM** - Konzeptentscheidung mit mehreren Optionen, kein Widerspruchs-/Sicherheitsfall, daher nicht HIGH. |
| Modellwechsel zum Vorgaenger | NEIN (BRIDGE-0073 lief ebenfalls auf Claude Opus 5 / MEDIUM) |
| depends_on | BRIDGE-0073 (ARCHIVED) |
| Gate | keines (reine Konzeptentscheidung, kein G2/G3/G4-Scope beruehrt) |
| stop_conditions | CONCEPT_CONFLICT |

> Ablauf: Claude Code `/acb-auftrag BRIDGE-0074` (Datei `.claude/commands/acb-auftrag.md`). Regeln: `docs/concepts/ACB-UMSETZUNGSKONZEPT-V2.md` §3.
> **MODELL-GATE:** erste Antwortzeile `MODELL: <x> / DENKSTUFE: <y>`. Abweichung von der Tabelle = STOPP.

## Auftrag

**Ziel:** Ein konkreter, **projektunabhaengiger** Formalisierungsvorschlag (Entscheidungsebene, keine Implementierung) fuer `OpenIssue` als das in BRIDGE-0073 §2 identifizierte einzige Objekt mit echtem Kontinuitaetsnutzen. Hintergrund: fuer das Projektprofil Dorfschaft werden ueber 1000 Steuerchat-Sitzungen erwartet; die Uebergabe gespeicherter Entscheidungen und offener fachlicher Aufgaben an den jeweils naechsten Steuerchat muss dabei token-sparsam erfolgen. Heute laeuft Kontinuitaet ausschliesslich ueber die volltextuelle `docs/handover/ACB-UEBERGABE-v<N>.md`, die laut `docs/ACB-STEUERCHAT-STANDARDSTART.md` §2 bei jeder Sitzung vollstaendig gelesen werden muss - das waechst mit der Zahl der Sitzungen und ist nicht gezielt filterbar. Die Loesung muss fuer **jedes** ACB-Projektprofil funktionieren, Dorfschaft ist nur der aktuell bekannte konkrete Bedarfsfall (gleiches Leitprinzip wie in BRIDGE-0073).

**Scope:** Neu: `docs/concepts/ENTSCHEIDUNG-OPENISSUE-FORMALISIERUNG.md` (max. 80 Zeilen). Sonst nichts. Kein Code, kein `schemas/`-Eintrag, keine Aenderung an bestehenden Handover-/Entscheidungs-Dateien.

1. Ist-Stand/Problem in 3-5 Saetzen festhalten: Freitext-Handover, Pflichtlektuere der gesamten Datei pro Sitzung, kein gezielter Filter auf offene vs. erledigte Punkte, kein Mechanismus, der mit der Sitzungszahl skaliert.
2. Anforderungen an eine formalisierte Loesung ableiten und einzeln benennen:
   - **Strukturiert statt Prosa:** maschinell filterbar (z. B. nur offene Punkte, nur ein Projekt) statt vollstaendiger Volltext-Lektuere.
   - **Minimale Pflichtfelder je offenem Punkt:** Status (offen/erledigt), Kurzbezug, Entstehungs-`bridge_task_id` bzw. projektfremdes Pendant ueber `task_prefix` (`schemas/project.schema.yaml`), Entstehungsdatum/-sitzung.
   - **Generisch:** keine Projekt-Fachwerte (keine Dorfschaft-Kapitel-/Phasen-/K1-K6-Werte o. ae.) - gleiches Leitprinzip wie BRIDGE-0073 Punkt 3.
   - **Vereinbar mit Fail-Closed-Prinzip:** geschlossene Enums wo sinnvoll, keine pauschale Schema-Aufweichung (BRIDGE-0073 §4 Befund: ACB ist durchgaengig fail-closed - das bleibt so).
3. Mindestens zwei, hoechstens drei konkrete Formalisierungsoptionen ausarbeiten, nach demselben Muster wie `docs/concepts/ENTSCHEIDUNG-AUDIT.md`:
   - **A - eigenes Objekt:** neues `schemas/open-issue.schema.yaml` + eigener Store-Bereich (z. B. `open-issues/<project_id>/<id>.yaml`), ueber Bridge-CLI verwaltet.
   - **B - Erweiterungsfeld:** `result.schema.yaml` (oder `task.schema.yaml`) um ein optionales, strukturiertes `open_issues[]`-Feld ergaenzen statt eigenes Objekt/Store.
   - **C - maschinenlesbares Handover-Frontmatter:** `docs/handover/ACB-UEBERGABE-v<N>.md` um einen strukturierten YAML-Frontmatter-Block ergaenzen (offene Punkte als Liste), Freitext-Teil bleibt bestehen.
   Fuer jede Option: Aufwand als T-Shirt-Groesse (S/M/L, kein Zeitplan), Vor-/Nachteile bzgl. Token-Ersparnis bei sehr hoher Sitzungszahl, Vereinbarkeit mit dem Generizitaetsprinzip, Folgen fuer bestehenden Lesecode (`docs/ACB-STEUERCHAT-STANDARDSTART.md` §2, `docs/ACB-STEUERCHAT-ARBEITSWEISE.md` §1).
4. Empfehlung mit Begruendung aussprechen. Status der Datei: ENTWURF - Freigabe durch April noch ausstehend (wie bei allen bisherigen `ENTSCHEIDUNG-*.md`).
5. Ausdruecklich NICHT Teil dieses Auftrags: Implementierung (Schema- oder Code-Aenderung), Dorfschaft-Adapter-Inhalt, Neubewertung von G5, MULTI-AGENT-Ausfuehrungsfreigabe (bleibt eigener, spaeterer ACB-Auftrag, siehe BRIDGE-0073 §5).

**Tests:** Keine.

- [x] Ist-Stand/Problem in 3-5 Saetzen benannt
- [x] Anforderungen (strukturiert, Pflichtfelder, generisch, fail-closed-vereinbar) einzeln aufgefuehrt
- [x] Mindestens zwei Formalisierungsoptionen mit T-Shirt-Groesse, Vor-/Nachteilen und Generizitaets-Check
- [x] Empfehlung mit Begruendung, Status ENTWURF
- [x] Keine Dorfschaft-Fachwerte, kein Schema/Code geaendert
