# BRIDGE-0098: Tree-sitter-Spike

| Feld | Wert |
|---|---|
| Rechte | keine Repo-Schreibrechte noetig fuer den Spike selbst - Dokumentation wird committet |
| Scope | `docs/concepts/TREE-SITTER-SPIKE-ERGEBNIS.md`, dieses Arbeitspaket |

## Anlass

`DREI-SCHICHTEN-ARCHITEKTUR-SPEZIFIKATION.md` (BRIDGE-0094) nennt Tree-sitter
als bevorzugten, aber nicht einzig zulaessigen Kandidaten fuer den
Symbol-/Datei-Graph. Offene Frage vor einer Implementierungsentscheidung:
deckt Tree-sitter die fuer Dorfschaft (PHP 8.x, natives JavaScript,
PowerShell-Skripte) benoetigten Kantentypen tatsaechlich ab, und existiert
ueberhaupt eine PowerShell-Grammatik?

## Entscheidung zum Umfang (bewusste Abgrenzung)

Reiner Machbarkeits-Spike in einem **isolierten venv ausserhalb des Repos**
(`/tmp/.../spike-treesitter`, nicht in `requirements.txt`, nicht im
Repo-`.venv`) - bewusst getrennt von produktivem Code, da noch keine
Implementierungsentscheidung getroffen wurde. Kein Store-/CLI-Code, keine
Integration in ACB. Ergebnis fliesst nur als Dokumentation ins Repo.

## Vorgehen

1. PyPI-Verfuegbarkeit geprueft: `tree-sitter` (0.26.0), `tree-sitter-php`
   (0.25.1), `tree-sitter-javascript` (0.25.0), `tree-sitter-powershell`
   (0.26.4) - alle vorhanden. `tree-sitter-languages` (Sammelpaket) existiert
   NICHT mehr auf PyPI, daher Einzelpakete verwendet.
2. Drei repraesentative Beispieldateien erstellt, angelehnt an den von April
   genannten Dorfschaft-Stack: PHP-Klasse mit `extends`/`implements`/
   `trait use`/`require`/`require_once`/`include_once`/`namespace use`;
   JS-Modul mit `import`/`export`/Klassenvererbung; PowerShell-Skript mit
   Dot-Sourcing, `Import-Module`, Funktionsdefinition, Cmdlet-Aufrufen.
3. Parser-Skript (`spike.py`) lief gegen alle drei Dateien, Kantenextraktion
   gegen die in BRIDGE-0094 Abschnitt 4 geforderten Kantentypen geprueft.

## Ergebnis

Alle drei Grammatiken parsen die Beispiele fehlerfrei (`has_error=False`).
Alle geforderten Kantentypen extrahierbar:

- **PHP**: `REQUIRES` (require/require_once/include/include_once),
  `USES_NAMESPACE` (use-Deklaration), `EXTENDS`, `IMPLEMENTS`, `USES_TRAIT`.
- **JavaScript**: `IMPORTS` (alle drei Import-Formen: named/default/
  namespace), `EXPORTS`, Klassenvererbung.
- **PowerShell**: `DOT_SOURCES` (`. $Pfad`), `IMPORTS_MODULE`
  (`Import-Module`), `CALLS` (Cmdlet-/Funktionsaufrufe),
  `DEFINES_FUNCTION`.

**Parser-Eigenheit (dokumentierter Fund):** In der PHP-Grammatik sind
`base_clause` (extends) und `class_interface_clause` (implements) ueber
`child_by_field_name()` NICHT erreichbar (liefert `None`), obwohl das
offizielle Feld so benannt waere - Zugriff musste stattdessen ueber den
Kind-Knotentyp direkt erfolgen (`[c for c in node.children if c.type == ...]`).
Relevant fuer eine spaetere Implementierung: Feldnamen-Zugriff ist bei dieser
Grammatikversion nicht durchgaengig verlaesslich, Typ-basierter Zugriff als
Fallback einplanen.

**Fazit:** Tree-sitter deckt alle in BRIDGE-0094 geforderten Kantentypen fuer
den realen Dorfschaft-Stack ab, inklusive PowerShell (Grammatik existiert und
funktioniert). Kein Ausschlussgrund gefunden. Eine Implementierungsentscheidung
(welche Kanten tatsaechlich gespeichert werden, Ablageform im Symbol-Graph)
bleibt ein eigener, hier nicht getroffener Folgeauftrag.

## Akzeptanzkriterien

- [x] PyPI-Verfuegbarkeit aller vier benoetigten Pakete bestaetigt
  (inkl. PowerShell-Grammatik, offene Frage aus BRIDGE-0094)
- [x] Isoliertes venv, keine Repo-/`requirements.txt`-Verschmutzung
- [x] Drei repraesentative Beispiele (PHP/JS/PowerShell) gegen den
  genannten Dorfschaft-Stack
- [x] Alle in BRIDGE-0094 Abschnitt 4 geforderten Kantentypen je Sprache
  nachweislich extrahiert
- [x] Parser-Eigenheiten/Grenzen dokumentiert (Feldnamen-Fund)
- [x] Ergebnis als eigenes Dokument im Repo festgehalten, Scope-Abgrenzung
  (kein Implementierungscode) explizit begruendet
