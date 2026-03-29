# Easy Wallbox Adapter

Der Adapter ist speziell EVCC in Verbindung mit E3/DC Hauskraftwerken gedacht. Dieser Adapter simuliert die Wallbox-Kommunikation und stellt die in EVCC verfügbaren Messwerte und Daten fuer E3/DC bereit.

### Stand der Arbeit

Aktuell arbeitet der Adapter als Simulation einer Wallbox. Die Messwerte fuer Ladeleistung und Energie koennen aus EVCC per MQTT uebernommen werden. Die Topics können aber auch von jedem anderen Programm gefüllt werden.

### Einrichtung

Repository klonen und die Konfiguration ueber Umgebungsvariablen setzen. Fuer den Direktstart ohne Docker koennen die Defaults in `ewa.py` weiter verwendet werden, sinnvoller ist aber die Steuerung per Env-Variablen und ein Start per Docker.

### Docker

Es gibt jetzt ein `Dockerfile` und eine `compose.yaml`.

Start mit Docker Compose:
* `docker compose up --build -d`

Der Modbus-Server ist danach auf Port `502` des Hosts erreichbar. Die Konfiguration erfolgt ueber die Environment-Eintraege in `compose.yaml` oder ueber eine `.env` Datei im Projektverzeichnis.
Als Vorlage liegt eine `.env.example` bei.

Wenn dein MQTT-Broker nicht als Container-Service `mqtt` im selben Compose-Projekt laeuft, musst du `EWA_MQTT_HOST` anpassen.

### E3/DC

In E3/DC kann nach erfolgreichem Start von EWA im Meue über Wallbox die Wallbox als "Easy Connect Wallbox" hinzugefuegt werden.

Falls sich eine andere Wallbox bereits im System befindet und über Modbus erreichbar ist, (Speziell Wallbe) darf aber nicht die Funktion Durchsuchen verwendet werden, sondern nur die Direkteingabe der IP, da sonst E3/DC die eigentliche Wallbox versucht zu verbinden und ggfls. die Einstellungsparameter dieser verändert.

### EVCC per MQTT

`ladeleistung`, `energieaktuell` und `energietotal` werden aus EVCC per MQTT gelesen.

Standardmaessig werden folgende EVCC-Topics verwendet:
* `evcc/loadpoints/1/chargePower` - aktuelle Ladeleistung in W
* `evcc/loadpoints/1/chargedEnergy` - geladene Energie der aktuellen Session in Wh
* `evcc/loadpoints/1/chargeTotalImport` - Zaehlerstand des Ladepunkts in Wh

Zusatzlich werden weitere Loadpoint-Werte aus `evcc/loadpoints/1/#` uebernommen:
* `connected` -> `autoangesteckt`
* `charging` -> `laedt`
* `enabled` -> `freigegeben`
* `maxCurrent` -> `ladestrom`
* `phasesActive` -> aktive Phasen
* `chargeCurrents/1..3` -> Phasenstroeme
* `chargeVoltages/1..3` -> Phasenspannungen
* `chargeDuration` -> Ladezeit

Hinweis: EVCC veroeffentlicht keinen separaten Lock-Status. `entriegelt` wird deshalb in der Simulation aus `connected` abgeleitet.

Wichtige Umgebungsvariablen:
* `EWA_MQTT_HOST`, `EWA_MQTT_PORT`, `EWA_MQTT_USERNAME`, `EWA_MQTT_PASSWORD`
* `EWA_EVCC_MQTT_TOPIC`, `EWA_EVCC_LOADPOINT_ID`
* `EWA_BIND_HOST`, `EWA_BIND_PORT`
* `EWA_MAC`, `EWA_SERIENNUMMER`, `EWA_IP`, `EWA_SUBNET`
* `EWA_LADESTROM`, `EWA_LADEKABEL`, `EWA_MAX_LADESTROM`
* `EWA_PHASES`

### Interaktive Eingabe

Das Programm unterstuetzt zu Testzwecken eine interaktive Eingabe, welche die Parameter waehrend des Betriebs aendern und abfragen kann. Im Container ist diese standardmaessig deaktiviert (`EWA_INTERACTIVE=false`).
* Damit kann zum Beispiel ein Ladevorgang gestartet oder beendet werden: `laedt=true` beziehungsweise `laedt=false`
* Mit `help` koennen alle Befehle angezeigt werden
* `exit` beendet das Programm

### Haftung

Es wird keine Haftung fuer Schaeden uebernommen, die beim Ausfuehren oder Verwenden des Adapters entstehen. Es gibt keine Funktionsgarantie.

### Lizenz

Die Verwendung des Adapters steht unter der MIT Lizenz.
