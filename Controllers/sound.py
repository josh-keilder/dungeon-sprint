import pygame, os
from globals import *
from settings_manager import SettingsManager


class SoundController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
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

        self._initialized = True

        self.settings_manager = SettingsManager()

    def _load_sfx(self, directory, target_dict):
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith((".wav", ".ogg")):
                    name = os.path.splitext(file)[0]
                    target_dict[name] = pygame.mixer.Sound(os.path.join(directory, file))

    def _load_bg_music(self, directory):
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith((".wav", ".ogg")):
                    name = os.path.splitext(file)[0]
                    self.bg_music[name] = os.path.join(directory, file)

    def play_sfx(self, name, volume=None):
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

    def play_music(self, name=None, loops=0, volume=None):

        if not self.settings_manager.get("bg_music_enabled"):
            return

        if pygame.mixer_music.get_busy():
            return

        if volume is None:
            volume = self.settings_manager.get("bg_music_volume")

        if name is None and self.music_queue:
            name = self.music_queue[self.current_track_index]

        # Play specific music
        if name in self.bg_music:
            pygame.mixer.music.load(self.bg_music[name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        else:
            print(f"Music track '{name}' not found")

    def play_next_track(self):
        if not self.music_queue:
            return

        self.current_track_index = (self.current_track_index + 1) % len(
            self.music_queue
        )
        new_track = self.music_queue[self.current_track_index]
        self.play_music(new_track, loops=0, volume=0.2)

    def stop_music(self):
        pygame.mixer.music.stop()

    def handle_events(self, event):
        if event.type == self.MUSIC_ENDED:
            self.play_next_track()

    def set_music_volume(self, volume):
        volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(volume)

    def set_game_sfx_volume(self, volume):
        volume = max(0.0, min(1.0, volume))
        for sound in self.sfx_game.values():
            sound.set_volume(volume)
        self.settings_manager.set("game_sfx_volume", volume)

    def set_menu_sfx_volume(self, volume):
        volume = max(0.0, min(1.0, volume))
        for sound in self.sfx_menu.values():
            sound.set_volume(volume)
        self.settings_manager.set("menu_sfx_volume", volume)
