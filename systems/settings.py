import os
import json
from typing import Any

FILENAME = "settings.json"

SETTINGS = {
    "fps_enabled": False,
    "full_screen_enabled": False,
    "music_volume": 0.5,
    "sfx_volume": 0.5,
}


def load_settings() -> None:
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as file:
                file_data = json.load(file)
                SETTINGS.update(file_data)
        except (json.JSONDecodeError, IOError):
            print("Warning: Settings file corrupted, using defaults.")


def save_settings() -> None:
    with open(FILENAME, "w") as file:
        json.dump(SETTINGS, file, indent=4)


def get_setting(setting_name: str) -> str:
    return SETTINGS.get(setting_name)


def set_setting(setting_name: str, setting_value: Any) -> None:
    SETTINGS[setting_name] = setting_value