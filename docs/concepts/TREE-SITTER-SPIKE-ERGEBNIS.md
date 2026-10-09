# Tree-sitter-Spike: Ergebnis (BRIDGE-0098)

Status: ABGESCHLOSSEN (Machbarkeitsnachweis, 2026-10-09)
Bezug: `DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md` Abschnitt 4 (Symbol-/Datei-Graph)
Details/Scope-Abgrenzung: `work-packages/BRIDGE-098.md`

## Fragestellung

Deckt Tree-sitter die fuer den Dorfschaft-Stack (PHP 8.x modular, natives
JavaScript, PowerShell-Deployment-/Pruefskripte) benoetigten Kantentypen ab -
und existiert ueberhaupt eine PowerShell-Grammatik (offene Frage aus
BRIDGE-0094)?

## Vorgehen

Isolierter Spike in einem repo-fremden venv (nicht in `requirements.txt`,
nicht im Repo-`.venv` - bewusst getrennt, da noch keine
Implementierungsentscheidung vorliegt). Drei Pakete einzeln installiert
(`tree-sitter-languages` als Sammelpaket existiert nicht mehr auf PyPI):

| Paket | Version |
|---|---|
| tree-sitter | 0.26.0 |
| tree-sitter-php | 0.25.1 |
| tree-sitter-javascript | 0.25.0 |
| tree-sitter-powershell | 0.26.4 |

Drei repraesentative Beispieldateien (PHP-Klasse mit extends/implements/
trait-use/require-Varianten/namespace-use, JS-Modul mit allen drei
Import-Formen plus Export, PowerShell-Skript mit Dot-Sourcing/
Import-Module/Funktionsdefinition/Cmdlet-Aufrufen) wurden geparst und auf
die in Abschnitt 4 geforderten Kantentypen geprueft.

## Ergebnis

Alle drei Grammatiken parsen fehlerfrei. Alle geforderten Kantentypen
extrahierbar:

| Sprache | Kantentypen (nachgewiesen) |
|---|---|
| PHP | REQUIRES (require/require_once/include/include_once), USES_NAMESPACE, EXTENDS, IMPLEMENTS, USES_TRAIT |
| JavaScript | IMPORTS (named/default/namespace), EXPORTS, Klassenvererbung |
| PowerShell | DOT_SOURCES, IMPORTS_MODULE, CALLS, DEFINES_FUNCTION |

### Dokumentierter Parser-Fund

In der aktuellen PHP-Grammatik (`tree-sitter-php` 0.25.1) sind
`base_clause` (extends) und `class_interface_clause` (implements) ueber
`node.child_by_field_name(...)` **nicht** erreichbar (liefert `None`),
obwohl das jeweilige Feld inhaltlich so heisst. Workaround: Zugriff ueber
den Kind-Knotentyp direkt (`[c for c in node.children if c.type == "..."]`)
statt ueber Feldnamen. Fuer eine spaetere Implementierung einplanen:
typ-basierter Zugriff als Fallback, nicht blind auf Feldnamen verlassen.

## Fazit

Kein Ausschlussgrund gegen Tree-sitter als Parser-Basis fuer den
Symbol-/Datei-Graph (Schicht 2 der Drei-Schichten-Architektur) gefunden -
auch PowerShell ist abgedeckt. Offen und bewusst **nicht** Teil dieses
Spikes: die Implementierungsentscheidung selbst (welche Kanten tatsaechlich
dauerhaft gespeichert werden, Ablageform/Store-Anbindung des
Symbol-Graphen) - eigener Folgeauftrag.
