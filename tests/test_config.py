import os
import pytest
from config import Configuration


@pytest.fixture
def temp_config():
    """Erstellt eine temporäre Config-Datei für den Test und löscht sie danach."""
    test_filename = "test_temporary_config.json"
    config = Configuration(filename=test_filename)
    yield config

    # Aufräumen: Testdatei nach dem Test wieder löschen
    if os.path.exists(test_filename):
        os.remove(test_filename)


def test_default_values(temp_config):
    """Testet, ob die Standardwerte korrekt geladen werden."""
    assert temp_config.get_current_mode() == "Football"
    assert temp_config.get_volume_string() == "normal"


def test_volume_rotation(temp_config):
    """Testet, ob die Lautstärke leise → normal → laut → leise rotiert."""
    # Start ist "normal" (Wert aus Init)
    assert temp_config.set_volume_step("normal") == "normal"

    # 1. Klick → sollte "laut" werden
    next_step = temp_config.set_volume_step("laut")
    assert next_step == "laut"
    assert temp_config.get_volume_value() == 1.0

    # 2. Klick → sollte wieder auf "leise" springen
    next_step = temp_config.set_volume_step("leise")
    assert next_step == "leise"
    assert temp_config.get_volume_value() == 0.2