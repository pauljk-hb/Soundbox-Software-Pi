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
        self.history = []
        self.linear_index = 0

    @abstractmethod
    def get_next_sound(self) -> str | None:
        """Sucht den nächsten abzuspielenden Sound heraus."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Gibt den Namen der Strategie zurück (z.B. 'Football')."""
        pass

    def _get_next_file(self, playback_mode: str = "shuffle") -> str | None:
        """
        Sucht den nächsten Song basierend auf dem eingestellten Modus
        (shuffle oder linear) heraus.
        """
        if not os.path.exists(self.sound_dir):
            print(f"Verzeichnis nicht gefunden: {self.sound_dir}")
            return None

        # Alle Dateien einlesen und alphabetisch sortieren (wichtig für den linearen Modus!)
        all_files = sorted([
            os.path.join(self.sound_dir, f)
            for f in os.listdir(self.sound_dir)
            if f.endswith(('.mp3', '.wav'))
        ])

        if not all_files:
            return None

        # --- MODUS: LINEAR ---
        if playback_mode == "linear":
            # Falls der Index durch das Löschen/Hinzufügen von Dateien ungültig geworden ist, zurücksetzen
            if self.linear_index >= len(all_files):
                self.linear_index = 0

            chosen_file = all_files[self.linear_index]

            # Index für das nächste Mal hochzählen (rotierend am Ende wieder auf 0)
            self.linear_index = (self.linear_index + 1) % len(all_files)
            return chosen_file

        # --- MODUS: SHUFFLE (Deine bewährte Logik) ---
        else:
            allowed_files = [f for f in all_files if f not in self.history]
            if not allowed_files:
                allowed_files = all_files

            chosen_file = random.choice(allowed_files)
            self.history.append(chosen_file)
            if len(self.history) > 2:
                self.history.pop(0)

            return chosen_file


