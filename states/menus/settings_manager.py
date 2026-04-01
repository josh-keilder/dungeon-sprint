import os
import json


class SettingsManager:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, filename="settings.json"):

        if self._initialized:
            return

        self.filename = filename

        self.settings = {
            "fps_enabled": False, 
            "bg_music_enabled": True, 
            "volume": 0.5
        }

        self.load_settings()

        self._initialized = True

    def load_settings(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    file_data = json.load(f)

                    self.settings.update(file_data)
            except (json.JSONDecodeError, IOError):
                print("Warning: Settings file corrupted, using defaults.")

    def save_settings(self):
        with open(self.filename, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
