# SoundBox Software für Raspberry Pi

Eine robuste, autarke Jukebox-Software, entwickelt für die Ausführung auf einem Raspberry Pi. Das System ermöglicht es, Soundeffekte (z. B. Touchdown-Hymnen, Schiedsrichterpfiffe) über einen einzigen robusten Arcade-Button zu triggern. Dank eines integrierten, rein akustischen Sprachmenüs (Voice Menu) lässt sich die Box komplett ohne Display oder Netzanbindung konfigurieren.

---

## Features

- **Single-Button-Steuerung:** Alle Kernfunktionen (Sounds abspielen, Menü steuern) werden über einen einzigen Hardware-Button bedient.
- **Asynchrones Klick-Management:** Ein intelligenter Entprell- und Zählmechanismus unterscheidet präzise zwischen Einzelklicks, Doppelklicks und Dreifachklicks.
- **Akustisches Einstellungsmenü:** Ein zweistufiges Sprachmenü führt den Benutzer komplett über Audio-Ansagen durch die Konfiguration.
- **Modulare Strategien:** Leicht erweiterbar für verschiedene Sportarten durch das *Strategy Pattern*.
- **Persistente Speicherung:** Einstellungen (Modus, Lautstärke, Lichteffekte) werden direkt in einer JSON-Datei gesichert und überleben jeden Neustart.
- **Systemd-Integration:** Läuft als automatisierter Linux-Hintergrunddienst direkt aus einer virtuellen Python-Umgebung (`.venv`).

---

## System-Architektur & Module

Die Software folgt dem Prinzip der strikten Separation of Concerns (Trennung von Zuständigkeiten). Sie ist in folgende Kernmodule unterteilt:

```
SportSoundSoftware/
├── main.py
├── config.py
├── hardware.py
├── engine.py
└── strategies/
    ├── init.py
    └── base.py
```

### 1. `main.py` (Einstiegspunkt)
Der Dirigent der Anwendung. Sie initialisiert die Konfiguration, startet die Kern-Engine und verknüpft die Hardware-Events mit den entsprechenden Callback-Funktionen. Sie sorgt für den sauberen Start und hält das Skript am Laufen.

### 2. `config.py` (Daten & Kapselung)
Dieses Modul ist für die gesamte Datenhaltung zuständig. 
- Es lädt und speichert die `config.json`.
- Es verwaltet die verschachtelte **Baumstruktur des Menüs** (IDs, Namen und Pfade zu den System-Sounds).
- **Kapselung:** Die `config.py` bietet dedizierte Methoden (z. B. `toggle_current_mode()`, `increase_volume()`), sodass andere Module niemals direkt auf das rohe Daten-Dictionary zugreifen müssen.

### 3. `hardware.py` (Hardware-Abstraktion)
Die Brücke zur echten Welt unter Verwendung von `gpiozero` und `lgpio`.
- **Input (Button):** Registriert Klicks auf dem GPIO-Pin komplett asynchron. Ein Timer wartet nach dem ersten Klick kurz ab (Timeout), um aufeinanderfolgende Klicks zu zählen (z. B. 3 Klicks für das Menü).
- **Output (LED):** Steuert die LED im Arcade-Button. Sie unterstützt Dauerleuchten, Pulsieren für den Menümodus und schnelles Fehlerblinken.
- **Entprellung:** Hardwareseitiges Signalrauschen (Bouncing) wird über Software-Filter abgefangen.

### 4. `engine.py` (Zustandsmaschine & Logik)
Das Gehirn der Software. Hier läuft die Zustandsmaschine (`Normaler Modus` vs. `Menümodus`) und verwaltet den Cooldown nach Sound-Wiedergaben.
- **Im normalen Modus:** Leitet Klicks an die aktuell aktive Sport-Strategie weiter und spielt über `pygame.mixer` zufällige oder spezifische Sounds ab.
- **Im Menümodus:** Verwaltet die Navigation durch die zwei Menüebenen anhand der Klickanzahl.

### 5. `strategies/` (Modi-Verhalten)
Hier wird das *Strategy Pattern* angewendet. Jede Sportart kapselt ihre eigene Logik, welche Sounds bei einem Klick getriggert werden.
- `FootballStrategy`: Verwaltet z. B. Pfade zu Football-Sounds (`/home/soundbox/sounds/football`).
- `SoccerStrategy`: Verwaltet z. B. Pfade zu Fußball-Sounds (`/home/soundbox/sounds/soccer`).

---

## Bedienungskonzept (Voice Menu)

Da die Box auf dem Platz blind bedient wird, steuert man das System intuitiv über Klick-Muster:

### Normaler Modus
- **1x Klick:** Triggert einen Sound der aktuellen Sportart (mit anschließendem Cooldown).
- **3x Klick:** Öffnet das Einstellungsmenü $\rightarrow$ Sprachausgabe sagt: *"Einstellungen"*.

### Menümodus (Ebene 1 - Hauptmenü)
- **1x Klick:** Blättert zum nächsten Punkt (rotierend). Der Punkt wird laut vorgelesen (*"Modi"*, *"Lautstärke"*, *"Button Licht"*, *"Menü verlassen"*).
- **2x Klick (Doppelklick):** Wählt den aktuellen Punkt aus. Bei *Modi*, *Lautstärke* oder *Licht* springt das System tiefer in die **Ebene 2**.

### Menümodus (Ebene 2 - Untermenü)
- **1x Klick:** Blättert durch die Optionen der jeweiligen Einstellung (z. B. bei Lautstärke: *"Leise"*, *"Normal"*, *"Laut"*).
- **2x Klick (Doppelklick):** Bestätigt die Auswahl. Der Parameter wird sofort dauerhaft gespeichert, die Änderung aktiv gesetzt (z. B. Mixer-Lautstärke angepasst) und das **gesamte Menü automatisch geschlossen**.

---

## Hardware-Pinbelegung (BCM Layout)

Die Software nutzt die `lgpio`-Bibliothek auf Basis des Broadcom (BCM) Nummerierungsschemas.

| Komponente | GPIO (Code) | Physischer Pin am Pi | Gegenpol (GND) |
| :--- | :---: | :---: | :---: |
| **Arcade-Button** | `GPIO 17` | Pin 11 | Pin 9 |
| **LED (Pluspol)** | `GPIO 18` | Pin 12 | Pin 14 (über Widerstand) |

---

## Installation & Autostart

### 1. Abhängigkeiten installieren
Für das Kompilieren der C-Bibliothek des Hardware-Treibers werden `swig` und `liblgpio` benötigt:
```bash
sudo apt update
sudo apt install swig liblgpio-dev -y
```

### 2. Virtuelle Umgebung einrichten

```bash
cd /home/soundbox/SportSoundSoftware
python3 -m venv .venv
source .venv/bin/activate
pip install rpi-lgpio pygame gpiozero

```

### 3. Hintergrunddienst (Autostart) einrichten
Die Software wird über einen systemd-Service verwaltet. Die Konfiguration unter `/etc/systemd/system/stadion.service` sieht wie folgt aus:

```bash
[Unit]
Description=Snack Stadion Sound System
After=network.target

[Service]
Type=simple
User=soundbox
WorkingDirectory=/home/soundbox/SportSoundSoftware
ExecStart=/home/soundbox/SportSoundSoftware/.venv/bin/python /home/soundbox/SportSoundSoftware/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

```

**Dienst aktivieren und starten:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable stadion.service
sudo systemctl start stadion.service

```
## Erforderliche Ordnerstruktur für Sounds
Damit die Audiowiedergabe funktioniert, müssen folgende Ordner auf dem Pi existieren und mit entsprechenden .mp3-Dateien befüllt sein:
```
/home/soundbox/sounds/
├── football/          # Deine Football-Effekte
├── soccer/            # Deine Fußball-Effekte
└── system/            # 10 Pflicht-Dateien für das Sprachmenü:
                       # einstellungen.mp3, modus.mp3, lautstaerke.mp3, led.mp3, back.mp3
                       # football_aktiv.mp3, fussball_aktiv.mp3
                       # leise.mp3, normal.mp3, laut.mp3, an.mp3, aus.mp3
```

