"""
System: Sound and Audio Management
----------------------------------
A Singleton controller that manages the loading, playback, and volume control
of sound effects (SFX) and background music. It interfaces with the
SettingsManager to ensure user audio preferences are persisted.

Classes:
    SoundController: Manages audio channels, track queuing, and asset loading.
"""

import pygame
import os
from globals import *
from settings_manager import SettingsManager
from typing import Dict, List, Optional, Any


class SoundController:
    _instance = None

    def __new__(cls) -> "SoundController":
        """Ensures only one instance of SoundController exists."""
        if cls._instance is None:
            cls._instance = super(SoundController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initializes the mixer, audio dictionaries, and track queues."""
        if self._initialized:
            return

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.sfx_game = {}
        self.sfx_menu = {}
        self.bg_music = {}
        self.music_queue = []
        self.current_track_index = 0

        self.MUSIC_ENDED = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_ENDED)

        self._load_sfx("Assets/Sounds/Game", self.sfx_game)
        self._load_sfx("Assets/Sounds/Menu", self.sfx_menu)
        self._load_bg_music("Assets/Music")

        self.music_queue = list(self.bg_music.keys())
        self.settings_manager = SettingsManager()
        self._initialized = True

    def _load_sfx(
        self, directory: str, target_dict: Dict[str, pygame.mixer.Sound]
    ) -> None:
        """Iterates through a directory to load supported audio files into a dictionary."""
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith((".wav", ".ogg")):
                    name = os.path.splitext(file)[0]
                    target_dict[name] = pygame.mixer.Sound(
                        os.path.join(directory, file)
                    )

    def _load_bg_music(self, directory: str) -> None:
        """Maps music track names to their respective file paths for streaming."""
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith((".wav", ".ogg")):
                    name = os.path.splitext(file)[0]
                    self.bg_music[name] = os.path.join(directory, file)

    def play_sfx(self, name: str, volume: Optional[float] = None) -> None:
        """Plays a sound effect from the game or menu cache at a specified volume."""
        if name in self.sfx_game:
            if volume is None:
                volume = self.settings_manager.get("game_sfx_volume")
            sound = self.sfx_game[name]
            sound.set_volume(volume)
            sound.play()

        elif name in self.sfx_menu:
            if volume is None:
                volume = self.settings_manager.get("menu_sfx_volume")
            sound = self.sfx_menu[name]
            sound.set_volume(volume)
            sound.play()
        else:
            print(f"Sound '{name}' not found")

    def play_music(
        self, name: Optional[str] = None, loops: int = 0, volume: Optional[float] = None
    ) -> None:
        """Streams a background music track, respecting the user's enabled settings."""
        if not self.settings_manager.get("bg_music_enabled"):
            return

        if pygame.mixer_music.get_busy() and name is None:
            return

        if volume is None:
            volume = self.settings_manager.get("bg_music_volume")

        if name is None and self.music_queue:
            name = self.music_queue[self.current_track_index]

        if name in self.bg_music:
            pygame.mixer.music.load(self.bg_music[name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        else:
            print(f"Music track '{name}' not found")

    def play_next_track(self) -> None:
        """Increments the track index and plays the next song in the queue."""
        if not self.music_queue:
            return

        self.current_track_index = (self.current_track_index + 1) % len(
            self.music_queue
        )
        new_track = self.music_queue[self.current_track_index]
        self.play_music(new_track, loops=0)

    def stop_music(self) -> None:
        """Halts the current music stream."""
        pygame.mixer.music.stop()

    def handle_events(self, event: pygame.event.Event) -> None:
        """Listens for the end of a music track to trigger the next track in the queue."""
        if event.type == self.MUSIC_ENDED:
            self.play_next_track()

    def set_music_volume(self, volume: float) -> None:
        """Adjusts the volume of the current music stream (clamped between 0.0 and 1.0)."""
        volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(volume)

    def set_game_sfx_volume(self, volume: float) -> None:
        """Updates the volume for all game-related SFX and persists the setting."""
        volume = max(0.0, min(1.0, volume))
        for sound in self.sfx_game.values():
            sound.set_volume(volume)
        self.settings_manager.set("game_sfx_volume", volume)

    def set_menu_sfx_volume(self, volume: float) -> None:
        """Updates the volume for all menu-related SFX and persists the setting."""
        volume = max(0.0, min(1.0, volume))
        for sound in self.sfx_menu.values():
            sound.set_volume(volume)
        self.settings_manager.set("menu_sfx_volume", volume)
