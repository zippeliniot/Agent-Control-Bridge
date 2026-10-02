# Entscheidung: Formalisierung `OpenIssue`

**Status:** FREIGEGEBEN (Option A), 02.10.2026. BRIDGE-0074, kein Gate.
Grundlage: `ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md` §2 (`OpenIssue` als einziges Objekt mit
echtem Kontinuitaetsnutzen). Entscheidungsebene, keine Implementierung. **Projektunabhaengig:**
Dorfschaft ist nur der bekannte Bedarfsfall (ueber 1000 erwartete Steuerchat-Sitzungen), nicht
der Zuschnitt. Keine Projekt-Fachwerte in dieser Datei.

## 1. Ist-Stand / Problem

Kontinuitaet laeuft heute ausschliesslich ueber die volltextuelle
`docs/handover/ACB-UEBERGABE-v<N>.md`, die laut `docs/ACB-STEUERCHAT-STANDARDSTART.md` §2 und
`docs/ACB-STEUERCHAT-ARBEITSWEISE.md` §1 bei **jeder** Sitzung vollstaendig gelesen werden muss
("von Anfang bis Ende lesen — nicht ueberfliegen"). Offene und erledigte Punkte stehen dort als
Prosa gemischt (v13 §2 "Offene Entscheidung von April", §5 "Nicht von selbst anfangen bei",
§6 "Offene Punkte aus v12") — ohne maschinellen Filter auf "nur offen" oder "nur ein Projekt".
Jede neue Version traegt die offenen Punkte der Vorgaengerversion **von Hand** weiter; ein nicht
abgeschriebener Punkt verschwindet lautlos. Die Dateigroesse ist heute unkritisch (v13: 4.994
Byte) — das Problem ist nicht Volumen, sondern **Pflichtlektuere ohne Filter plus handgetragene
Fortschreibung**, und genau das skaliert nicht mit der Sitzungszahl.

## 2. Anforderungen

- **Strukturiert statt Prosa.** Maschinell filterbar nach Status und `project_id`, statt
  vollstaendiger Volltext-Lektuere.
- **Minimale Pflichtfelder je Punkt:** Status (offen/erledigt), Kurzbezug, Entstehungs-ID
  (`bridge_task_id`, bzw. projektfremdes Pendant ueber `task_prefix`/`project_task_id`,
  `schemas/project.schema.yaml`), Entstehungsdatum bzw. -sitzung.
- **Status nachtraeglich aenderbar.** Entstehung und Abschluss liegen in verschiedenen Sitzungen.
- **Generisch.** Keine Projekt-Fachwerte (Kapitel-, Phasen-, Konfliktklassen-Werte o. ae.) —
  gleiches Leitprinzip wie BRIDGE-0073 Punkt 3.
- **Fail-closed-vereinbar.** Geschlossene Enums wo sinnvoll, `additionalProperties: false` wie
  ueberall sonst; keine pauschale Schema-Aufweichung (BRIDGE-0073 §4).

## 3. Optionen

**A — Eigenes Objekt.** Neues `schemas/open-issue.schema.yaml`, Store
`open-issues/<project_id>/<id>.yaml`, Verwaltung ueber Bridge-CLI (anlegen, schliessen, listen),
Muster wie `tasks/<id>/task.yaml`.
- Aufwand: **M** (Schema + Store + CLI-Unterbefehle + Tests).
- Token: beste Skalierung — gelesen wird nur die Liste der **offenen** Punkte; ihre Groesse haengt
  an der Zahl offener Punkte, nicht an der Zahl vergangener Sitzungen.
- Generizitaet: erfuellt (`project_id` + `task_prefix`, keine Fachwerte).
- Lesecode: `STANDARDSTART` §2 und `ARBEITSWEISE` §1 bekommen den Schritt "offene Punkte per CLI
  abfragen"; der Prosa-Abschnitt "Offene Punkte" der Uebergabedatei wird vom Traeger zum Verweis,
  die Fortschreibung von Hand entfaellt.

**B — Erweiterungsfeld.** Optionales, strukturiertes `open_issues[]` in `result.schema.yaml`
(alternativ `task.schema.yaml`), kein eigenes Objekt, kein eigener Store.
- Aufwand: **S** (ein Schemafeld + Tests).
- Token: Ersparnis nur beim Erfassen. Zum Lesen muessten **alle** `results/*/result.yaml` aller
  Laeufe durchsucht werden — die Leselast waechst mit der Sitzungszahl, also genau falsch herum.
- Generizitaet: erfuellt.
- **Strukturelle Schwaeche:** Ergebnisse sind je Lauf unveraenderlich abgelegt. Ein Punkt, der in
  Lauf 12 entsteht und in Lauf 400 geschlossen wird, kann dort nicht auf "erledigt" gesetzt werden
  — die dritte Anforderung aus §2 ist damit nicht erfuellbar. B taugt als **Erfassungskanal**,
  nicht als Register.

**C — Maschinenlesbares Handover-Frontmatter.** `docs/handover/ACB-UEBERGABE-v<N>.md` erhaelt
einen YAML-Frontmatter-Block mit den offenen Punkten; der Freitext-Teil bleibt.
- Aufwand: **S** (Konvention + Lesehinweis, kein Store, kein CLI).
- Token: sofortige Ersparnis — der Sitzungsstart liest den Block statt der ganzen Datei.
- Generizitaet: erfuellt, aber ohne projektuebergreifende Sicht (ein Block je Uebergabedatei).
- **Strukturelle Schwaeche:** die Punkte werden weiter je Sitzung in die naechste Version
  **abgeschrieben** — der Ausfallgrund aus §1 (lautloser Verlust) bleibt, nur strukturiert.

## 4. Empfehlung

**Option A.** Nur A erfuellt alle fuenf Anforderungen aus §2, insbesondere die nachtraegliche
Statusaenderung, an der B scheitert, und die Entkopplung von der handgetragenen Fortschreibung,
an der C scheitert. C ist mit S billiger, loest aber den eigentlichen Ausfallgrund nicht — bei
der erwarteten Sitzungszahl ist das eine Scheinersparnis, weil der Verlust offener Punkte mit
jeder Weitergabe wahrscheinlicher wird. A ist das einzige Modell, dessen Leselast nicht mit der
Sitzungszahl waechst.

Umsetzung als eigenes, spaeteres Arbeitspaket (Schema + Store + CLI + Tests); `open_issues[]` aus
B kann dort spaeter als optionaler Erfassungskanal ergaenzt werden, ersetzt das Register aber
nicht. Nicht Teil dieser Entscheidung: Implementierung, Projekt-Adapter-Inhalte, Neubewertung von
G5, MULTI-AGENT-Ausfuehrungsfreigabe (eigener, spaeterer Auftrag, siehe
`ENTSCHEIDUNG-STEERING-CONTINUITY-ABGLEICH.md` §5).
