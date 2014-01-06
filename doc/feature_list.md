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

# Keyboard Shortcuts
Play/Pause: strg+leer
Fast Forward: strg+f
Quit: Esc
