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

Ausserdem gibt es noch RewardsController, ShapesController und StateFeatureController.
Bei diesen handelt es sich um die Auswahl der aktivierten Funktionen bzw. Shapes.
Das besondere hier ist, dass die verfuegbaren Features anhand der Methoden in den jeweiligen Modulen (reward_features.py und features.py) geparsed und befuellt werden.

### Zusammenspiel zwischen der GUI und dem Agenten
Die Oberflaeche und der Agent laufen jeweils in einem eigenen Thread. Wobei die
GUI als Haupt-Thread gestartet wird und anschließend eine Instanz des Agenten
in einem weiteren Thread startet.
Die Kommunikation zwischen den Threads findet mittels Events statt. Wird
beispielsweise in der GUI der Pause-Button gedrueckt, wird das resume_event auf
'unset' gesetzt und der Agent haelt seine Ausfuehrung an bis das Event erneut
ausgeloest wird. Neben dem resume_event gibt es noch das stop_event um die
Anwendung zu beenden und das wait_for_update_event. Das letztere sorgt in der
Schritt-fuer-Schritt Anzeige dafuer, dass der Agent nach jedem Schritt anhaelt
und auf die Aktualisierung der GUI wartet. Erst wenn die GUI meldet, das der
naechste Schritt erfolgen soll, wird fortgefahren.
Die GUI wird mittels einer Refreshfunktion 'after()' des TKInter Frameworks in
regelmaessigen Abstaenden aktualisiert.

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
In dem features.py enthalten sind Features, die den State beschreiben. Alle Funktionen
in diesem Modul werden automatisch im State-Features-Fenster aufgelistet.

TODO weitere infos zu den features..

## reward_features.py
Im reward_features-Modul sind Features zu finden, die zur Berechnung der Reward 
verwendet werden koennen. Jede reward Funktion erhaelt beim Aufruf das Environment-Objekt, 
von dem es Daten abrufen kann. Alle Funktionen in diesem Modul werden automatisch im
Reward-Features-Fenster aufgelistet.

TODO mehr infos zu den rewards..

## util.py
TODO utils.. vllt ins gui-modul?

## settings.py
Die settings.py ist gedacht, um Einstellungen fuer die Anwendung zu halten, also
in der Regel fuer mehrere Module relevante Konstanten.
