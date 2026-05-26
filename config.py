import json
import os

class Configuration:
    def __init__(self, filename: str = "config.json"):
        self.filepath = filename
        self.data = {
            "mode": "Football",
            "volume": 0.8,
            "led_blink": True
        }
        self.load()

    def load(self):
        """Lädt die Einstellungen aus der JSON-Datei."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                print("Konfiguration erfolgreich geladen.")
            except Exception as e:
                print(f"Fehler beim Laden der Config, nutze Standards: {e}")

    def save(self):
        """Speichert die aktuellen Einstellungen in die JSON-Datei."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            print("Konfiguration erfolgreich gespeichert.")
        except Exception as e:
            print(f"Fehler beim Speichern der Config: {e}")