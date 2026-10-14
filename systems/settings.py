import json
import os
from typing import Any

SETTINGS_FILE_PATH = "settings.json"

SETTINGS = {
    "fps_enabled": False,
    "full_screen_enabled": False,
    "music_volume": 0.5,
    "sfx_volume": 0.5,
}


def load_settings() -> None:
    if os.path.exists(SETTINGS_FILE_PATH):
        try:
            with open(SETTINGS_FILE_PATH, "r") as settings_file:
                saved_settings = json.load(settings_file)
                SETTINGS.update(saved_settings)
        except (json.JSONDecodeError, IOError):
            print("Warning: Settings file corrupted, using defaults.")


def save_settings() -> None:
    with open(SETTINGS_FILE_PATH, "w") as settings_file:
        json.dump(SETTINGS, settings_file, indent=4)


def get_setting(setting_name: str) -> str:
    return SETTINGS.get(setting_name)


def set_setting(setting_name: str, setting_value: Any) -> None:
    SETTINGS[setting_name] = setting_value