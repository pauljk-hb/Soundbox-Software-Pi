import pygame
import threading
import time
from strategies import FootballStrategy, SoccerStrategy
from config import Configuration


class SoundBoxEngine:
    def __init__(self):
        # 1. Einstellungen laden
        self.config = Configuration()

        # 2. Audio-Mixer initialisieren
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.config.get_volume_value())

        # 3. Strategien (Sportmodi) bereithalten
        self.strategies = {
            "Football": FootballStrategy(),
            "Fußball": SoccerStrategy()
        }

        # Aktuelle Strategie aus Config setzen (Fallback auf Football)
        current_mode = self.config.get_current_mode()
        self.current_strategy = self.strategies.get(current_mode, self.strategies["Football"])

        # 4. Status-Variablen
        self.hardware = None
        self.menu_mode = False
        self.cooldown_active = False
        self.cooldown_time = 2.0

    def register_hardware(self, hardware):
        self.hardware = hardware

    def get_current_mode_name(self) -> str:
        return self.current_strategy.get_name()

    def handle_button_clicks(self, click_count: int):
        print(f"Signal empfangen: {click_count} Klicks")

        # FALL 1: Wir sind im Menü-Modus
        if self.menu_mode:
            self._handle_menu(click_count)
            return

        # FALL 2: Normaler Modus (Sound abspielen)
        if click_count == 1:
            self._play_sound_event()
        elif click_count == 3:
            self._enter_menu_mode()

    def _play_sound_event(self):
        """Spielt asynchron einen Sound, falls kein Cooldown aktiv ist."""
        if self.cooldown_active or pygame.mixer.music.get_busy():
            print("Gesperrt: Sound läuft oder Cooldown aktiv.")
            return

        current_playback = self.config.get_playback_mode()
        sound_path = self.current_strategy.get_next_sound(current_playback)
        if not sound_path:
            print("Kein Sound in diesem Modus gefunden!")
            if self.hardware:
                self.hardware.blink_led(duration=1.0, speed=0.1)
            return

        # Sound in einem eigenen Thread abspielen, damit das Hauptprogramm frei bleibt
        threading.Thread(target=self._audio_playback_worker, args=(sound_path,), daemon=True).start()

    def _audio_playback_worker(self, sound_path: str):
        """Arbeitet im Hintergrund: Spielt Audio und regelt den Cooldown."""
        try:
            print(f"Spiele: {sound_path}")
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()

            # LED-Blink-Effekt während der Sound läuft (falls in Config erlaubt)
            if self.config.data.get("led_blink", True) and self.hardware:
                while pygame.mixer.music.get_busy() and not self.menu_mode:
                    self.hardware.set_led(False)
                    time.sleep(0.3)
                    self.hardware.set_led(True)
                    time.sleep(0.3)

            # Warten bis der Sound wirklich vorbei ist (falls das Blinken aus war)
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            # --- COOLDOWN START ---
            self.cooldown_active = True
            if self.hardware:
                self.hardware.set_led(False)  # Licht aus signalisiert: Cooldown

            time.sleep(self.cooldown_time)

        except Exception as e:
            print(f"Fehler im Audio-Worker: {e}")
        finally:
            self.cooldown_active = False
            if self.hardware and not self.menu_mode:
                self.hardware.set_led(True)

    def _enter_menu_mode(self):
        """Wird bei 3 Klicks im Hauptmodus aufgerufen (Eintritt Ebene 1)."""
        self.menu_mode = True
        self.menu_structure = self.config.get_menu_structure()

        self.menu_index = 0
        self.sub_menu_index = 0
        self.active_sub_items = []

        print("MENÜ MODUS AKTIVIERT!")
        if self.hardware:
            self.hardware.blink_led(duration=1.0, speed=0.2)

        self._play_system_sound("/home/soundbox/sounds/system/einstellungen.mp3")

    def _handle_menu(self, click_count: int):
        """Verarbeitet das komplette Menü basierend auf der aktuellen Ebene."""

        if self.active_sub_items:
            if click_count == 1:
                # 1 Klick: Im Untermenü weiterblättern
                self.sub_menu_index = (self.sub_menu_index + 1) % len(self.active_sub_items)
                current_sub = self.active_sub_items[self.sub_menu_index]
                print(f"  └── Unterpunkt: {current_sub['name']}")
                self._play_system_sound(current_sub["sound"])

            elif click_count == 2:
                # Doppelklick: Wert in Ebene 2 auswählen -> Parameter ändern & komplett beenden
                current_sub = self.active_sub_items[self.sub_menu_index]
                print(f"  └── Auswahl bestätigt: {current_sub['name']}")
                self._execute_sub_menu_action(current_sub["id"])

        else:
            if click_count == 1:
                # 1 Klick: Im Hauptmenü weiterblättern
                self.menu_index = (self.menu_index + 1) % len(self.menu_structure)
                current_main = self.menu_structure[self.menu_index]
                print(f"Hauptmenü: {current_main['name']}")
                self._play_system_sound(current_main["sound"])

            elif click_count == 2:
                # Doppelklick: Hauptpunkt auswählen
                current_main = self.menu_structure[self.menu_index]

                if current_main["id"] == "exit":
                    self._exit_menu()
                elif current_main["sub_items"]:
                    # Wenn Unterpunkte existieren -> Ebene 2 aktivieren!
                    self.active_sub_items = current_main["sub_items"]
                    self.sub_menu_index = 0
                    print(f"Wechsel in Untermenü für: {current_main['name']}")

                    # Direkt den ersten Punkt der 2. Ebene vorlesen
                    self._play_system_sound(self.active_sub_items[0]["sound"])

    def _execute_sub_menu_action(self, option_id: str):
        """Verarbeitet die finale Auswahl aus der 2. Ebene und schließt das Menü."""

        # Hauptmenü-Punkt herausfinden, zu dem wir gehören
        parent_id = self.menu_structure[self.menu_index]["id"]

        if parent_id == "mode":
            self.config.set_current_mode(option_id)
            self.current_strategy = self.strategies[option_id]
            print(f"Modus geändert auf: {option_id}")

        elif parent_id == "playback":
            # option_id ist hier "shuffle" oder "linear"
            self.config.set_playback_mode(option_id)
            print(f"Abspielmodus geändert auf: {option_id}")

        elif parent_id == "volume":
            self.config.set_volume_step(option_id)
            pygame.mixer.music.set_volume(self.config.get_volume_value())
            print(f"Lautstärke geändert auf: {option_id}")

        elif parent_id == "led":
            is_enabled = (option_id == "an")
            self.config.set_led_blink(is_enabled)
            print(f"LED Blinken bei Sound geändert auf: {is_enabled}")

        self._exit_menu()

    def _exit_menu(self):
        """Verlässt das Menü komplett."""
        self.menu_mode = False
        self.active_sub_items = []
        print("Menü geschlossen. Soundbox bereit.")
        if self.hardware:
            self.hardware.set_led(True)

    def _play_system_sound(self, sound_path: str):
        """Spielt Menü-Sounds sofort und ohne Cooldown ab."""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Fehler beim Abspielen des Menü-Sounds {sound_path}: {e}")
