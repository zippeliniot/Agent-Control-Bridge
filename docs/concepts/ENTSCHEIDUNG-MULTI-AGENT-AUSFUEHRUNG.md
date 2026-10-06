# Entscheidung: MULTI-AGENT-Ausfuehrungsfreigabe (Schreibkonfliktvermeidung)

**Status:** ENTWURF — Freigabe durch April ausstehend. BRIDGE-0076, kein Gate.
Getrennt von der fachlichen Festlegung aus BRIDGE-0073 Punkt 4f: dort ist der **Bedarf** an
paralleler Mehrfachbearbeitung bestaetigt, hier geht es allein um die **Ausfuehrungsfreigabe**.
Keine Implementierung, keine Aenderung an `claim.py`/`ENTSCHEIDUNG-RESSOURCENREGEL.md`, keine Projekt-Fachwerte.

## 1. Ist-Stand und Risiko

Der Schluessel der Ressourcenregel ist `(repository, remote, branch)` (`claim.py:124`
`_resource_key`), also repo-/branchweit und nicht artefaktweise: zwei Sitzungen am selben Branch
blockieren sich als `RESOURCE_CONFLICT`, auch wenn sie verschiedene Artefakte bearbeiten.
**Diese Sperre wirkt jedoch nur innerhalb eines Klons.** `_check_resource` (`claim.py:129`) scannt
ausschliesslich `results/*/claim.json` unterhalb des eigenen `root`; `claim.json` steht in keiner
`--commit`-Whitelist (`gitops.py:95-116`) und wurde nie versioniert, und der Writer-Lock liegt als
gitignorierte `.acb-writer.lock` je `root`. Zwei Klone am selben Branch — die Konvention
`projects/<projekt-id>` erlaubt beliebig viele — sehen die Claims des anderen nicht und laufen
faktisch bereits heute parallel. Verschaerfend: jede Store-Aktion schreibt und committet
`audit/audit.jsonl` (in **jeder** Whitelist, `gitops.py:99`), und der Writer-Lock serialisiert nur
die Store-Schreibmethoden — Arbeitsdateien, die ein Executor selbst editiert (`work-packages/`,
`docs/`), deckt er nicht ab.

**Befund:** Die Annahme, die heutige Regel schliesse echte Parallelausfuehrung strukturell aus,
gilt nur klonintern. Klonuebergreifend ist der Kanal offen; einzige Barriere bleibt Git
(Push-Reject bei non-fast-forward) — sichtbar, aber erst **nach** getaner Arbeit.

## 2. Optionen

**A — Vierter Schluesselbestandteil (Artefaktebene).** `_resource_key` wird um einen
adapterdefinierten, fuer ACB opaken Bestandteil erweitert (z. B. `resource_scope` aus dem
Auftrag), sodass gleicher Repo/Branch bei unterschiedlichem Scope zwei aktive Claims zulaesst.
- Aufwand **M** (Schluessel, Schemafeld, Claim- und Parallelitaetstests). Vorteil: parallele
  Claims ohne Branch-Wechsel, Granularitaet bestimmt der Adapter.
- Risiko: der Claim deckt genau die Dateien **nicht** ab, die den Konflikt tragen —
  `audit/audit.jsonl` bei jeder Aktion, dazu `work-packages/` und die Handover-Datei. Zwei
  erlaubte Claims duerfen dieselbe Arbeitsdatei schreiben; klonintern gilt Last-write-wins, denn
  der Writer-Lock greift nur im Store.

**B — A plus Positivliste parallelisierbarer Pfade.** Wie A, zusaetzlich entscheidet eine im
Projektprofil (`projects/<id>/project.yaml`) gepflegte **Positivliste**, welche Pfade parallel
bearbeitet werden duerfen; alles andere bleibt repo-/branchweit exklusiv.
- Aufwand **L** (A + Profilfeld + Pfadpruefung + Negativtests). Vorteil: Default-deny bleibt
  erhalten, gemeinsame Dateien sind per Konstruktion gesperrt.
- Risiko: zweiter Nebenlaeufigkeitsmechanismus neben Git, dauerhafte Pflegelast. Als
  **Ausnahmeliste** geteilter Dateien formuliert waere es Default-allow und kein Fail-Closed —
  eine vergessene gemeinsame Datei wird zum stillen Verlustkanal.

**C — Unveraendert: keine Parallelausfuehrung in ACB.** Die Ressourcenregel bleibt wie sie ist;
Parallelitaet entsteht ausserhalb: ein eigener Branch (und, wo gewuenscht, Klon) je Sitzung,
Zusammenfuehrung erst beim Cross-Check.
- Aufwand **S** (keine Codeaenderung, nur Konvention). Vorteil: der Schluessel enthaelt `branch` —
  verschiedene Branches kollidieren heute schon nicht, Konflikte werden mit vorhandenen Werkzeugen
  ausgetragen (Diff, Merge, Review), `audit/audit.jsonl` divergiert je Branch.
- Risiko: Merge-Aufwand, kein gemeinsamer Live-Stand waehrend der Parallelarbeit; die Luecke aus
  §1 bleibt und ist als eigener, kleiner Haertungsauftrag zu fuehren.

## 3. Fail-Closed- und Generizitaets-Check

| Option | Fail-closed? | Generisch? |
|---|---|---|
| A | **Nein.** Geteilte Dateien fallen aus der Pruefung; innerhalb eines Klons ist stiller Verlust einer Schreiboperation auf Arbeitsdateien moeglich (Writer-Lock deckt nur den Store). | Ja, solange der vierte Bestandteil ein fuer ACB opaker String aus dem Auftrag ist und ACB keine Pfadsemantik interpretiert. |
| B | **Ja, aber nur als Positivliste** (Default-deny). Als Ausnahmeliste: nein. Die Vollstaendigkeit der Liste ist nicht maschinell pruefbar und bleibt Pflegerisiko. | Ja, wenn die Liste im Projektprofil liegt und der Core keine Pfadnamen kennt. |
| C | **Ja**, unveraendert: ein Konflikt ist weiterhin ein harter `RESOURCE_CONFLICT` vor der Arbeit, ein Branch-Konflikt ein sichtbarer Merge-Konflikt. | Ja, trivial — keine Werte im Core. |

## 4. Empfehlung

**Option C.** Entscheidend ist nicht die Granularitaet des Claims, sondern dass der Claim die
konfliktbehafteten Dateien gar nicht schuetzt: `audit/audit.jsonl` wird bei jeder Aktion
geschrieben, Arbeitsdateien liegen ausserhalb des Writer-Locks. Eine Verfeinerung des Schluessels
erkauft damit keine Parallelitaet, sie verschiebt den Konflikt nur vom klaren Vorab-Fehler zum
spaeteren Merge-Konflikt oder, klonintern, zu stillem Last-write-wins. Der Branch ist bereits Teil
des Schluessels und traegt die gewuenschte Parallelitaet ohne Codeeingriff; damit bleibt
**MULTI-AGENT in ACB: NEIN**, waehrend der fachliche Bedarf per Branch-/Klon-Trennung erfuellbar
bleibt. Wird in-Repo-Parallelitaet spaeter doch verlangt, dann nur **A und B gemeinsam**, B als
Positivliste, zusaetzlich eine akteur- oder sitzungsgetrennte Audit-Ablage (Anknuepfung:
`ENTSCHEIDUNG-AUDIT.md` §2) — nie A allein. Davon unabhaengig gehoert die Luecke aus §1 in einen
eigenen, kleinen Haertungsauftrag, weil sie heute schon offen ist.

**Nicht Teil dieser Entscheidung:** Implementierung, Projekt-Adapter-Inhalte, G5-Bewertung,
Aenderungen an `claim.py` oder `ENTSCHEIDUNG-RESSOURCENREGEL.md`.
