from strategies.base import SoundStrategy

class FootballStrategy(SoundStrategy):
    def __init__(self, sound_dir: str = "/home/soundbox/sounds/football"):
        super().__init__(sound_dir)

    def get_next_sound(self, playback_mode: str = "shuffle") -> str | None:
        return self._get_next_file(playback_mode)

    def get_name(self) -> str:
        return "Football"


class SoccerStrategy(SoundStrategy):
    def __init__(self, sound_dir: str = "/home/soundbox/sounds/soccer"):
        super().__init__(sound_dir)

    def get_next_sound(self, playback_mode: str = "shuffle") -> str | None:
        return self._get_next_file(playback_mode)

    def get_name(self) -> str:
        return "Fußball"