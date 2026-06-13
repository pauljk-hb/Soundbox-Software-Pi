import json
import os


class Configuration:
    def __init__(self, filename: str = "config.json"):
        self.filepath = filename

        # Standard-Einstellungen, falls keine config.json existiert
        self.data = {
            "mode": "Football",
            "volume_step": "normal",
            "led_blink": True,
            "playback_mode": "shuffle"
        }

        self.menu_structure = [
            {
                "id": "mode",
                "name": "Modi",
                "sound": "/home/soundbox/sounds/system/modus.mp3",
                "sub_items": [
                    {"id": "Football", "name": "Football", "sound": "/home/soundbox/sounds/system/football_aktiv.mp3"},
                    {"id": "Fußball", "name": "Fußball", "sound": "/home/soundbox/sounds/system/fussball_aktiv.mp3"}
                ]
            },
            {
                "id": "playback",
                "name": "Abspielmodus",
                "sound": "/home/soundbox/sounds/system/abspielmodus.mp3",
                "sub_items": [
                    {"id": "shuffle", "name": "Zufall", "sound": "/home/soundbox/sounds/system/zufall.mp3"},
                    {"id": "linear", "name": "Linear", "sound": "/home/soundbox/sounds/system/linear.mp3"}
                ]
            },
            {
                "id": "volume",
                "name": "Lautstärke",
                "sound": "/home/soundbox/sounds/system/lautstaerke.mp3",
                "sub_items": [
                    {"id": "leise", "name": "Leise", "sound": "/home/soundbox/sounds/system/leise.mp3"},
                    {"id": "normal", "name": "Normal", "sound": "/home/soundbox/sounds/system/normal.mp3"},
                    {"id": "laut", "name": "Laut", "sound": "/home/soundbox/sounds/system/laut.mp3"}
                ]
            },
            {
                "id": "led",
                "name": "Button Licht",
                "sound": "/home/soundbox/sounds/system/led.mp3",
                "sub_items": [
                    {"id": "an", "name": "An", "sound": "/home/soundbox/sounds/system/an.mp3"},
                    {"id": "aus", "name": "Aus", "sound": "/home/soundbox/sounds/system/aus.mp3"}
                ]
            },
            {
                "id": "exit",
                "name": "Menü verlassen",
                "sound": "/home/soundbox/sounds/system/back.mp3",
                "sub_items": []  # Direktes Verlassen, kein Untermenü
            }
        ]
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
                print("Konfiguration erfolgreich geladen.")
            except Exception as e:
                print(f"Fehler beim Laden der Config, nutze Standards: {e}")

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            print("Konfiguration erfolgreich gespeichert.")
        except Exception as e:
            print(f"Fehler beim Speichern der Config: {e}")

    def get_menu_structure(self) -> list:
        return self.menu_structure

    def get_current_mode(self) -> str:
        return self.data.get("mode", "Football")

    def set_current_mode(self, mode_name: str):
        self.data["mode"] = mode_name
        self.save()

    def get_playback_mode(self) -> str:
        return self.data.get("playback_mode", "shuffle")

    def set_playback_mode(self, mode: str):
        self.data["playback_mode"] = mode
        self.save()

    def get_volume_string(self) -> str:
        return self.data.get("volume_step", "normal")

    def get_volume_value(self) -> float:
        mapping = {"leise": 0.2, "normal": 0.6, "laut": 1.0}
        return mapping.get(self.get_volume_string(), 0.6)

    def set_volume_step(self, step_name: str):
        self.data["volume_step"] = step_name
        self.save()

    def is_led_blink_enabled(self) -> bool:
        return self.data.get("led_blink", True)

    def set_led_blink(self, enabled: bool):
        self.data["led_blink"] = enabled
        self.save()