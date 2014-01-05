# Codestruktur

Der Code ist strukturiert in mehrere Module:

- gui.py
- agent.py
- features.py
- environment.py
- reward_features.py
- settings.py
- util.py

## gui.py
Die gui.py enthaelt alle Klassen, die fuer die visuelle Darstellung verantwortlich
sind. Ausserdem befindet sich hier die Ausfuehrungslogik.
Zum Starten der Anwendung wird dieses Modul ausgefuehrt (python gui.py)

Jedes Fenster der Anwendung hat einen Controller. Diese werden nach dem Schema
BlaController benannt. Das Hauptfenster wird durch den MainController gesteuert.
Dieser hat Zugriff auf das MainPanel, in welchem ein BoardFrame und ein ControlFrame
enthalten sind. Die Benamung wird hier auf die jeweiligen Komponententypen im
GUI-Framework TKinter zurueckgefuehrt.
Die Controller enthalten die jeweiligen Button-Callback-Routinen. Ausserdem
holen sie die relevanten Daten fuer die Fenster.

Im PlotController wird die Logik fuer den Graphen gehalten.

TODO wie funktioniert die Zusammenarbeit zw. gui und Agent :)
TODO der OptionsController existiert noch nicht in der Form.....
Das dritte Fenster ist das Options-Fenster. Hier kann man einstellen, welche
State- und Reward-Features verwendet werden sollen. Es wird vom OptionsController
verwaltet und vom OptionsDialog dargestellt. Das besondere hier ist, dass die
verfuegbaren Features anhand der Methoden in den jeweiligen Modulen (reward_features.py
und features.py) geparsed und befuellt werden.

## agent.py
Im agent-Modul werden die Klassen Agent und PerceivedState gehalten. Die Agent-Klasse
ist der aktive Part des Systems. Er erstellt vor jedem Zug ein Abbild des aktuellen
Zustands der Environment, den PerceivedState. Dieser wird anhand der ausgewaehlten
Features definiert und hilft dem Agenten, eine vereinfachte Sicht auf die Welt zu haben
und so die Wahrscheinlichkeit einer Wiedererkennung des Zustands zu erhoehen.
Ausserdem kann der Agent aus einer Auswahl verfuegbarer Aktionen in der Environment
waehlen und eine dieser Aktionen durchfuehren.

Der PerceivedState enthaelt eine beliebige Anzahl Features (>1), mit denen er den
Zustand modelliert. Diese Features sind Funktionen in der features.py.

## environment.py
Das environment-Modul enthaelt das Environment, das Field, die Action-Klasse und die Shape-Klassen.
Environment stellt die Welt dar, auf der der Agent arbeitet. Die Klasse hat Informationen
ueber den aktuellen Zustand des Spiels, enthaelt das Spielfeld und stellt moegliche Aktionen
bereit. Ueber das Environment werden Aktionen ausgefuehrt, die dann auf das Field uebertragen
werden. Ausserdem haelt es das aktuelle Shape.

Die Field-Klasse ist eine Repraesentation des Spielfeldes. Sie bietet dem Environment
Methoden zum platzieren von Shapes.
Die Action-Klasse wird als Datenobjekt fuer eine Aktion verwendet. Momentan enthaelt sie
Felder fuer die Spalte, in die der Stein fallengelassen werden soll, sowie die Rotation,
in der der Stein rotiert werden soll.

Die Shape-Klasse enthaelt Name des Shapes und Spalte in der das Shape spawned. Wenn
eine Aktion ausgefuehrt wird, wird das aktuelle Shape manipuliert und Schritt fuer
Schritt im Feld heruntergelassen, bis eine Kollision auftritt.
Die verschiedenen Shapes werden in den jeweiligen Unterklassen festgehalten. Diese
enthalten die Form des Shapes in den verschiedenen moeglichen Rotationen als Listen.

## features.py
TODO features..

## reward_features.py
TODO reward features..

## util.py
TODO utils.. vllt ins gui-modul?

## settings.py
Die settings.py ist gedacht, um Einstellungen fuer die Anwendung zu halten, also
in der Regel fuer mehrere Module relevante Konstanten.