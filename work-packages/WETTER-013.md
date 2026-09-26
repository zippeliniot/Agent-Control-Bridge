# WETTER-0013 - Schmale-Screens-Layout: Header-Ueberlappung + Kartenkopf-Umbruch sauber loesen

| Feld | Wert |
|---|---|
| bridge_task_id | WETTER-0013 |
| project_id | wetter-app |
| Typ / Klasse | BUGFIX |
| Rechte | WORKTREE_WRITE, TEST_EXECUTION, GIT_PUSH |
| **Modell / Denkstufe** | **Claude Sonnet 5 / MEDIUM** |
| depends_on | WETTER-0012 |
| Gate | keines |
| stop_conditions | SCOPE_VIOLATION, CONCEPT_CONFLICT |

> Laeuft im Klon `E:\_DEV\Agent-Control-Bridge\projects\wetter-app` (ACB-Koordination)
> und im Ziel-Repo `E:\_DEV\Wetter-App` (Branch main).
> **MODELL-GATE:** erste Antwortzeile "MODELL: <dein Modell> / DENKSTUFE: <deine Stufe>". Abweichung = STOPP.

## Ablauf (kein Slash-Befehl - /acb-auftrag ist nur fuer BRIDGE-IDs geschrieben)
Setze BR = .venv\Scripts\python.exe src\bridge\cli.py --root E:\_DEV\Agent-Control-Bridge\projects\wetter-app --schema-dir E:\_DEV\Agent-Control-Bridge\projects\wetter-app\schemas
Actor = claude-code
1. Im ACB-Repo: git pull. `BR task create` (project_id wetter-app, task_prefix WETTER, repository wetter-app, expected_head = aktueller HEAD von E:\_DEV\Wetter-App), dann `BR run start WETTER-0013 --actor claude-code --commit`, `git push`.
2. VORAB im Ziel-Repo E:\_DEV\Wetter-App: `git pull`, `git status` sauber, HEAD muss 17c8717d96247d3b18e0f11290d0209d70f214c9 sein (Stand nach WETTER-0012). Abweichung -> STOPP.
3. Scope NUR: `index.html`.

## Befund (Steuerchat, per Screenshot bestaetigt)
`.header-bar` (index.html, CSS-Regel ca. Zeile 19): `display: flex; align-items: center; justify-content: space-between;` OHNE `flex-wrap`. Der Haupt-Header (`#main-header`) hat zwei direkte Kinder: `.header-left` (Kein-Regen-Button + der neue Tanken-Button aus WETTER-0009) und eine rechte Gruppe (1-Tag/3-Tage-Umschalter + Zahnrad, inline gestylt ca. Zeile 154). Mit drei Buttons links UND dem Umschalter+Zahnrad rechts passt die Zeile auf schmalen Phones (siehe Screenshot: "1 Tag" ueberlappt direkt den "TANKEN"-Button) nicht mehr nebeneinander - kein Umbruch vorgesehen.

## Fix (NUR index.html, CSS)
1. `.header-bar`: `flex-wrap: wrap;` und `row-gap: 8px;` ergaenzen - bei zu wenig Platz rutscht die rechte Gruppe (Umschalter+Zahnrad) in eine zweite Zeile UNTER die linke Gruppe, statt zu ueberlappen. Bestehende Breakpoints/sonstige Eigenschaften unveraendert.
2. Zusaetzlich (deine Vorgabe "Auswahlbox 1 Tag/3 Tage muss kleiner werden"): im bereits vorhandenen `@media (max-width: 420px)`-Block (ca. Zeile 127) eine neue, spezifische Regel ergaenzen, NUR fuer den Haupt-Header-Umschalter (nicht die Taschensee-Tabs, die haben bereits eine eigene `.sw-tabs .range-btn`-Regel und bleiben unangetastet):
```css
   .header-bar .range-toggle .range-btn { padding: 6px 14px; font-size: 0.8rem; }
```
   (Selektor testweise anpassen, falls die tatsaechliche Verschachtelung im Markup abweicht - Hauptsache: nur der Header-Umschalter wird kleiner, keine anderen `.range-btn`-Vorkommen im Code.)
3. Keine Aenderung an Funktionalitaet/IDs/Klassen der Buttons selbst.

## Teil B - Kartenkopf-Umbruch sauber loesen (Temperatur/Wind/Taschensee/Ostsee)
Befund (Steuerchat, per Screenshot bestaetigt): `.chart-head` hat bereits `flex-wrap: wrap` (kein Ueberlappen dort), ABER auf schmalen Screens faellt der Werte+Legenden-Block (bei `#temp-current`, `#wind-current`, `#sw-current`, `#sea-current` jeweils ein Wrapper-Div mit Inline-Style `style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;"`) unkontrolliert in eine zweite Zeile und bleibt dabei rechtsbuendig/zentriert wirkend stehen (siehe Screenshot: "GR 14° · 0 mm" springt mittig unter den Titel) - wirkt nicht wie ein bewusstes Layout, sondern wie ein Bruch.

1. Die vier betroffenen Inline-Styles (`#temp-current`, `#wind-current`, `#sw-current`, `#sea-current` jeweils der umschliessende Wrapper-Div, NICHT die Spans selbst) durch eine gemeinsame neue CSS-Klasse ersetzen, z. B. `chart-head-value`:
```css
   .chart-head-value { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
```
   (gleiche Werte wie bisher inline, nur jetzt als Klasse - Funktionalitaet unveraendert.)
2. Im bestehenden `@media (max-width: 420px)`-Block ergaenzen:
```css
   .chart-head { flex-direction: column; align-items: flex-start; }
   .chart-head-value { align-items: flex-start; }
```
   Ergebnis: bei schmalen Screens steht der Titel oben, der Werte+Legenden-Block darunter - beides klar LINKSBUENDIG (statt des jetzigen unklaren Rechts-/Mittig-Sprungs). Bei >=420px bleibt das bisherige Nebeneinander-Layout unveraendert (KEINE Aenderung an der Basis-Regel von `.chart-head` ausserhalb des Media-Queries).
3. Keine Aenderung an der JS-Logik (`updateTempHeader`, `updateWindHeader`, `updateSeaHeader`, Taschensee-Header) - nur CSS/Markup-Klasse.

## Pflicht: echte Browser-Verifikation bei mind. 2 schmalen Breiten
`python -m http.server` im Ziel-Repo. Pruefe per Chrome-Tool bei simulierten Viewport-Breiten 360px und 390px (typische kleine iPhones):
1. Kein Ueberlappen mehr zwischen "Tanken"-Button und "1 Tag"/"3 Tage"-Umschalter - entweder bleibt alles in einer Zeile (wenn Platz reicht) oder die rechte Gruppe rutscht sauber in eine zweite Zeile darunter.
2. Umschalter-Buttons sichtbar kleiner als vorher bei <420px.
3. Alle vier Kartenkoepfe (Temperatur, Wind, Taschensee, Ostsee): bei <420px stehen Titel oben und Wert+Legende darunter, beides sauber linksbuendig - kein mittiger/rechtsbuendiger Sprung mehr.
4. Taschensee-Tabs (Aktuell/Woche/Monat/Jahr/Vergleich) unveraendert - Regressionscheck, da die neue Regel NICHT `.sw-tabs .range-btn` treffen darf.
5. Bei normaler Desktop-Breite (>=1200px): Header UND alle vier Kartenkoepfe sehen weiterhin wie bisher aus (keine unnoetige zweite Zeile, Werte weiterhin rechtsbuendig neben dem Titel).
6. Browser-Konsole ohne Fehler.

## Abschluss
`BR run finish WETTER-0013 --status COMPLETED --actor claude-code --commit --summary "<HEAD-SHA, Teil-A/B-Befund je Breite, Regressionscheck>"`, `git push`.
Ausgabe NUR: Footer + max. 5 Zeilen: ACB-HEAD, Ziel-Repo-HEAD, Teil-A-Befund, Teil-B-Befund, Regressionscheck.
- [ ] Teil A: flex-wrap ergaenzt, kein Ueberlappen mehr bei 360px/390px, Umschalter bei <420px kleiner
- [ ] Teil B: alle 4 Kartenkoepfe bei <420px sauber linksbuendig gestapelt, Desktop-Ansicht unveraendert
- [ ] Taschensee-Tabs unveraendert (Regressionscheck)
- [ ] Scope eingehalten (nur index.html)
