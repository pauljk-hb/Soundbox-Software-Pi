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
        pygame.mixer.music.set_volume(self.config.data["volume"])

        # 3. Strategien (Sportmodi) bereithalten
        self.strategies = {
            "Football": FootballStrategy(),
            "Fußball": SoccerStrategy()
        }

        # Aktuelle Strategie aus Config setzen (Fallback auf Football)
        current_mode = self.config.data.get("mode", "Football")
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

        sound_path = self.current_strategy.get_next_sound()
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
        self.menu_mode = True
        print("MENÜ MODUS AKTIVIERT! (1 = Weiter, 2 = Bestätigen)")
        if self.hardware:
            self.hardware.blink_led(duration=1.5, speed=0.5)

    def _handle_menu(self, click_count: int):
        if click_count == 1:
            # Strategie durchrotieren
            current_name = self.current_strategy.get_name()
            if current_name == "Football":
                self.current_strategy = self.strategies["Fußball"]
            else:
                self.current_strategy = self.strategies["Football"]
            print(f"🔄 Modus gewechselt zu: {self.current_strategy.get_name()} (Noch nicht gespeichert!)")
            if self.hardware:
                self.hardware.blink_led(duration=0.4, speed=0.1)

        elif click_count == 2:
            # Bestätigen und Speichern
            new_mode = self.current_strategy.get_name()
            self.config.data["mode"] = new_mode
            self.config.save()
            self.menu_mode = False
            print(f"💾 Gespeichert! Modus ist jetzt fest: {new_mode}")
            if self.hardware:
                self.hardware.set_led(True)