import pygame, os
from globals import *

class SoundController:
    _instance = None  # This stores the "one and only" version

    def __new__(cls):
        # If an instance doesn't exist yet, create it
        if cls._instance is None:
            cls._instance = super(SoundController, cls).__new__(cls)
            # Put your initialization logic here so it only runs ONCE
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.sfx = {}
        self.bg_music = {}
        self.music_queue = []
        self.current_track_index = 0

        self.MUSIC_ENDED = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_ENDED)
        
        self._load_sfx("Assets/Sounds")
        self._load_bg_music("Assets/Music")


        self.music_queue = list(self.bg_music.keys())

        self._initialized = True

    def _load_sfx(self, directory):
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith((".wav", ".ogg")):
                    name = os.path.splitext(file)[0]
                    self.sfx[name] = pygame.mixer.Sound(os.path.join(directory, file))
    
    def _load_bg_music(self, directory):
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith((".wav", ".ogg")):
                    name = os.path.splitext(file)[0]
                    self.bg_music[name] = os.path.join(directory, file)

    def play_sfx(self, name, volume = 0.5):
        if name in self.sfx:
            sound = self.sfx[name]
            sound.set_volume(volume)
            sound.play()
        else:
            print(f"Sound '{name}' not found")

    def play_music(self, name, loops=0, volume = 0.5):
        # If name is None, it plays the current track in the cue
        if name is None and self.music_queue:
            name = self.music_queue[self.current_track_index]

        if name in self.bg_music:
            pygame.mixer.music.load(self.bg_music[name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        else:
            print(f"Music track '{name}' not found")

    def play_next_track(self):
        if not self.music_queue: 
            return
        
        self.current_track_index = (self.current_track_index + 1) % len(self.music_queue)
        new_track = self.music_queue[self.current_track_index]
        self.play_music(new_track, loops=0, volume=-0.5)

    def stop_music(self):
        pygame.mixer.music.stop()

    def handle_events(self, event):
        if event.type == self.MUSIC_ENDED:
            self.play_next_track()
