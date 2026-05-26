import threading
import time
from gpiozero import Button, LED


class InputOutputHandler:
    def __init__(self, button_pin: int, led_pin: int, click_callback):
        self.led = LED(led_pin)
        # bounce_time verhindert Hardware-Prellen
        self.button = Button(button_pin, bounce_time=0.05)
        self.click_callback = click_callback  # Funktion, die aufgerufen wird, wenn Klicks fertig gezählt sind

        self.click_count = 0
        self.timer = None
        self.click_window = 0.4  # Zeitfenster in Sekunden, um Mehrfachklicks zu sammeln

        # Event an den Button hängen
        self.button.when_pressed = self._on_button_pressed
        self.led.on()  # Standardmäßig bereit

    def _on_button_pressed(self):
        """Wird bei JEDEM physischen Knopfdruck sofort aufgerufen."""
        self.click_count += 1

        # Wenn der Timer läuft, warten wir noch ab.
        # Wenn nicht, starten wir einen neuen Thread-Timer für das Zeitfenster.
        if self.timer is None or not self.timer.is_alive():
            self.timer = threading.Timer(self.click_window, self._evaluate_clicks)
            self.timer.start()

    def _evaluate_clicks(self):
        """Wird nach Ablauf des Zeitfensters im Hintergrund aufgerufen."""
        final_clicks = self.click_count
        self.click_count = 0  # Zurücksetzen für das nächste Mal

        # Leite die Anzahl der Klicks an die Haupt-Engine weiter
        if self.click_callback:
            self.click_callback(final_clicks)

    def set_led(self, status: bool):
        """Schaltet die LED an oder aus."""
        if status:
            self.led.on()
        else:
            self.led.off()

    def blink_led(self, duration: float, speed: float = 0.2):
        """Lässt die LED für eine gewisse Zeit blinken, ohne den Hauptthread zu blockieren."""

        def _blink():
            end_time = time.time() + duration
            while time.time() < end_time:
                self.led.toggle()
                time.sleep(speed)
            self.led.on()  # Danach wieder an

        threading.Thread(target=_blink, daemon=True).start()