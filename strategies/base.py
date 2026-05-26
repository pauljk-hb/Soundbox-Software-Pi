from abc import ABC, abstractmethod
import os
import random


class SoundStrategy(ABC):
    """
    Abstrakte Basisklasse für alle Sound-Strategien.
    Jeder neue Sond-Modus MUSS diese Methoden implementieren.
    """

    def __init__(self, sound_dir: str):
        self.sound_dir = sound_dir

    @abstractmethod
    def get_next_sound(self) -> str | None:
        """Sucht den nächsten abzuspielenden Sound heraus."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Gibt den Namen der Strategie zurück (z.B. 'Football')."""
        pass

    def _get_random_file(self) -> str | None:
        """
        Hilfsmethode, die von den Kindklassen genutzt werden kann.
        Sucht eine zufällige Audio-Datei aus dem Verzeichnis.
        """
        if not os.path.exists(self.sound_dir):
            print(f"Verzeichnis nicht gefunden: {self.sound_dir}")
            return None

        files = [
            os.path.join(self.sound_dir, f)
            for f in os.listdir(self.sound_dir)
            if f.endswith(('.mp3', '.wav'))
        ]

        return random.choice(files) if files else None