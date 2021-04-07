# Easy Wallbox Adapter

Der Adapter ist speziell für Wallbe ECO 2.0s - Wallboxen in Verbindung mit E3/DC - Hauskraftwerken gedacht. In den Wallbe-Wallboxen befinden sich keine Verbrauchszähler, weshalb ein einbinden zwar trotzdem möglich ist, jedoch die Steuerung des E3/DC nicht ermöglicht. Dieser Adapter soll die Einbindung eines beliebigen Erzeugungszählers ermöglichen und somit alle Funktionen einer normalen E3/DC - Wallbox zur Verfügung stellen.

### Stand der Arbeit

Aktuell arbeitet der Adapter nur als Simulation einer Wallbox. Man kann ihn in E3/DC ohne eine zur Verfügung stehende Wallbox einbinden und Ladungen damit simulieren. Eine Anbindung an eine echte Wallbox geht noch nicht.

### Einrichtung

Respository klonen, EInstellungen in ewa.py setzen (Seriennummer, Mac und IP), ggfls. Firewall für Port 502 öffnen.

### Interaktive Eingabe

Das Programm unterstützt zu Testzwecken eine Interaktive Eingabe, welche die Parameter während des Betriebs ändern und Abfragen kann.
* Damit kann z.B. ein Ladevorgang gestartet oder beendet werden: *laedt=true* bzw. *laedt=false*
* Mit *help* können alle Befehle angezeigt werden
* *exit* beendet das Programm

### Haftung

Es wird keine Haftung für Schäden die beim Ausführen oder verwenden des Adapters entstehen übernommen. Es gibt auch keine Funktionsgarantie.
:bomb: 

### Lizenz

Die Verwendung des Adapters steht unter der MIT Lizenz, kann also jederzeit in anderen Projekten verwendet oder angepasst werden.

### Unterstützung

Immer gerne gesehen :smile: 