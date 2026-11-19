import json
import os

# Current settings: the game's defaults, with the saved values for those same settings
# merged over them
SETTINGS = {}
_file_path = None  # set by load_settings


def load_settings(defaults, file_path):
    global _file_path
    _file_path = file_path
    SETTINGS.clear()
    SETTINGS.update(defaults)

    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as settings_file:
                saved = json.load(settings_file)
                SETTINGS.update(
                    {name: value for name, value in saved.items() if name in defaults}
                )
        except (json.JSONDecodeError, IOError):
            print("Warning: Settings file corrupted, using defaults.")


def save_settings():
    with open(_file_path, "w") as settings_file:
        json.dump(SETTINGS, settings_file, indent=4)


def get_setting(setting_name):
    return SETTINGS.get(setting_name)


def set_setting(setting_name, setting_value):
    SETTINGS[setting_name] = setting_value
