```text
 __           __                                                           __      
/\ \__       /\ \__         __                                            /\ \__   
\ \ ,_\    __\ \ ,_\  _ __ /\_\    ____         __       __      __    ___\ \ ,_\  
 \ \ \/  /'__`\ \ \/ /\`'__\/\ \  /',__\      /'__`\   /'_ `\  /'__`\/' _ `\ \ \/  
  \ \ \_/\  __/\ \ \_\ \ \/ \ \ \/\__, `\    /\ \L\.\_/\ \L\ \/\  __//\ \/\ \ \ \_ 
   \ \__\ \____\\ \__\\ \_\  \ \_\/\____/    \ \__/.\_\ \____ \ \____\ \_\ \_\ \__\
    \/__/\/____/ \/__/ \/_/   \/_/\/___/      \/__/\/_/\/___L\ \/____/\/_/\/_/\/__/
                                                         /\____/                   
                                                         \_/__/                    

```
# Installation

## Ubuntu 14.10

Voraussetzungen: 

- Evtl: sudo apt-get install libfreetype6-dev python-dev
- sudo apt-get install python-tk python-matplotlib

- hg clone ssh://hg@bitbucket.org/timsn/tetrisagent
- cd tetrisagent

- sudo -H pip install -r requirements.txt --allow-external BitVector --allow-unverified BitVector


## Mac OSX

Voraussetzungen: python, mercurial

- hg clone ssh://hg@bitbucket.org/timsn/tetrisagent
- cd tetrisagent
- sudo easy_install pip (might be unnecessary depending on python installation)
- sudo -H pip install -r requirements_osx.txt --allow-external BitVector --allow-unverified BitVector

## Anmerkung
Wir wollen eigentlich ein Docker file verwenden, um die Installation zu erleichtern.
# Ausführung
python gui.py

# Keyboard Shortcuts
Play/Pause: strg+leer

Fast Forward: strg+f

Quit: Esc

# Featureumfang der Anwendung
Bei Tetrisagent handelt es sich um eine Anwendung, in der ein Agent mittels Techniken des Reinforcement Learnings bei einer vereinfachten Form eines Tetrisspiels Aktionen auswaehlen und ausfuehren kann und so selbststaendig besser werden soll. Mittels der graphischen Oberflaeche kann man diesen Lernfortschritt ueberwachen und viele Einstellungen veraendern.
Der Agent arbeitet mit dem Q-Learning-Algorithmus. Mittels Features werden die Zustaende modelliert und die Rewards berechnet. 	

## Featureliste
Der Tetrisagent verfuegt ueber folgende wesentliche Features.

### GUI
- Einstellbare State- und Rewardfeatures
- Auswahl der verfuegbaren Shapes
- langsame Ausfuehrung des Spiels sowie Vorspulen mit Limit der CPU-Kapazitaet (nur 1 CPU-Core)
- Statistik-Werte zur Analyse
- einstellbare Variablen alpha, gamma, epsilon
- Speicherung der zuletzt verwendeten Einstellungen
- Speichern und Laden eines Durchlaufes mit Q-Tabelle und Statistik-Werten
- Graph mit Bloecken pro Iteration
- Automatisches parsen der State- und Rewardfeatures
- Keyboard Shortcuts

### Tetris
- Alle Standardshapes mit allen Rotationsmoeglichkeiten
- uebliche Game Over-Szenarien
- nur "Fallenlassen", kein "einschieben" von Steinen in Luecken moeglich

### Agent
- Q-Learning mit eigener PerceivedState-Klasse, die mittels Features den Zustand modelliert.

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
# Ausblick
Im Folgenden sind einige Vorschlaege fuer weitere Features, die hinzugefuegt werden koennten.
Ausserdem sind unten weitere moegliche Experimente aufgelistet, die vielversprechend sein koennten.

## Tetrisfeatures
- Spielen gegen den Bot
- bewegen der Steine beim Drop

## GUI
- Steindrop animieren
- weitere Moeglichkeiten zur besseren Fortschrittsvisualisierung
- Schriftgroesse und Elemente fuer Praesentationen skalierbar machen
- Graph in eigenem Fenster anzeigen
- einige Einstellungen in Optionsfenster verschieben
- Variablen waehrend der Ausfuehrung laufend veraenderbar machen (z.B. Epsilon ueber n Durchlaeufe von 0 bis 1 fliessend veraendern)

## Algorithmus
- andere Algorithmen verwenden (z.B. Q-Lambda)
- moeglicherweise weitere zustandsmodellierende und Reward-Features implementieren
- neuronales Netz

## Testing
- Verbesserung der Testmoeglichkeiten (z.B. mehrmaliges laufen bei gleichen Settings, automatisiertes Testen von mehreren Szenarien)

## Experimente
TODO

## Bugs
- Wenn im Shape-Auswahlfenster kein Shape ausgewaehlt wird, wird die leere Liste dennoch uebernommen und beim naechsten Ausfuehren kommt es zu einem Fehler und die Anwendung muss neu gestartet werden.


# Ressourcensammlung

- [Carr: Adapting RL to Tetris](http://research.ict.ru.ac.za/g02c0108/CSHnsThesis.pdf)
- [Carr: Applying RL to Tetris](http://www.cs.ru.ac.za/research/g02C0108/files/litreviewfinalhandin.pdf)
- [Saad: Analysis of different RL Techniques on Tetris](http://www.cs.unm.edu/~pdevineni/papers/Saad.pdf)
- [Klein: RL Folien (Features)](http://inst.eecs.berkeley.edu/~cs188/fa10/slides/FA10%20cs188%20lecture%2012%20--%20reinforcement%20learning%20II%20(6PP).pdf)
- [RL Lecture](http://www.youtube.com/watch?v=ifma8G7LegE)
- [Sutton: Reinforcement Learning Book](http://webdocs.cs.ualberta.ca/~sutton/book/the-book.html)

- [Implementationsgrundlage Tetris-Tk](https://code.google.com/p/tetris-tk/)

