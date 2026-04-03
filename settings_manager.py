"""
System: Settings Management
---------------------------
Implements a persistent settings system using the Singleton pattern.
This ensures a single source of truth for game configurations (volume,
display, etc.) that can be accessed across different game states.

Classes:
    SettingsManager: Handles loading, saving, and accessing JSON-based settings.
"""

import os
import json


class SettingsManager:
    _instance = None

    def __new__(cls):
        """Ensures only one instance of SettingsManager exists."""
        if not cls._instance:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, filename="settings.json"):
        if self._initialized:
            return

        self.filename = filename

        # Default configuration values
        self.settings = {
            "fps_enabled": False,
            "full_screen_enabled": False,
            "bg_music_enabled": True,
            "bg_music_volume": 0.5,
            "game_sfx_volume": 0.5,
            "menu_sfx_volume": 0.5,
        }

        self.load_settings()
        self._initialized = True

    def load_settings(self):
        """Reads settings from the local JSON file and merges them with defaults."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    file_data = json.load(f)
                    # update() merges file data into defaults to handle missing keys
                    self.settings.update(file_data)
            except (json.JSONDecodeError, IOError):
                print("Warning: Settings file corrupted, using defaults.")

    def save_settings(self):
        """Serializes current settings to the JSON file with pretty printing."""
        with open(self.filename, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        """Returns the value for a given key, or None if the key doesn't exist."""
        return self.settings.get(key)

    def set(self, key, value):
        """Updates a setting value and immediately persists it to disk."""
        self.settings[key] = value
        self.save_settings()
