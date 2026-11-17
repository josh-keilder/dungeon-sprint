import json
import os

# The settings file, saved in the project root (git-ignored)
SETTINGS_FILE_PATH = "settings.json"

# Current settings; starts as the defaults, then the saved file is merged over it
SETTINGS = {
    "fps_enabled": False,
    "full_screen_enabled": False,
    "screen_shake_enabled": True,
    "music_volume": 0.5,
    "sfx_volume": 0.5,
}


def load_settings():
    if os.path.exists(SETTINGS_FILE_PATH):
        try:
            with open(SETTINGS_FILE_PATH, "r") as settings_file:
                saved_settings = json.load(settings_file)
                SETTINGS.update(saved_settings)
        except (json.JSONDecodeError, IOError):
            print("Warning: Settings file corrupted, using defaults.")


def save_settings():
    with open(SETTINGS_FILE_PATH, "w") as settings_file:
        json.dump(SETTINGS, settings_file, indent=4)


def get_setting(setting_name):
    return SETTINGS.get(setting_name)


def set_setting(setting_name, setting_value):
    SETTINGS[setting_name] = setting_value
