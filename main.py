import time
import sys
from engine import SoundBoxEngine
from hardware import InputOutputHandler

# Hardware-Pins definieren
GPIO_BUTTON = 17
GPIO_LED = 18

def main():
    print("--------------------------------------------------")
    print("SOUNDBOX WIRD GESTARTET...")
    print("--------------------------------------------------")

    engine = SoundBoxEngine()

    hardware = InputOutputHandler(
        button_pin=GPIO_BUTTON,
        led_pin=GPIO_LED,
        click_callback=engine.handle_button_clicks
    )

    engine.register_hardware(hardware)

    print("--------------------------------------------------")
    print(f"Jukebox aktiv! Aktueller Modus: {engine.get_current_mode_name()}")
    print("--------------------------------------------------")

    # Hauptschleife (Main Thread)
    try:
        while True:
            # Da die Button-Erkennung und Audio asynchron in eigenen Threads laufen,
            # muss der Hauptthread hier nur am Leben bleiben und kann z.B. CPU sparen.
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nBeende Soundbox...")
        hardware.set_led(False)
        sys.exit(0)

if __name__ == "__main__":
    main()