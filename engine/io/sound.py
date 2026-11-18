import os

import pygame

# Audio files a folder may hold; each is named by its filename without extension
AUDIO_EXTENSIONS = (".wav", ".ogg")

# Loaded audio: sound effects as Sound objects, music as file paths (streamed)
SFX = {}
MUSIC = {}

# Playback state
_current_sfx_volume = 0.5
_current_music_volume = 0.5
_current_music_name = None


def load_sfx(folder):
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename.endswith(AUDIO_EXTENSIONS):
                name = os.path.splitext(filename)[0]
                SFX[name] = pygame.mixer.Sound(os.path.join(folder, filename))


def load_music(folder):
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename.endswith(AUDIO_EXTENSIONS):
                name = os.path.splitext(filename)[0]
                MUSIC[name] = os.path.join(folder, filename)


def play_sfx(name, volume=None):
    if name in SFX:
        sound = SFX[name]
        if volume is None:
            volume = _current_sfx_volume

        sound.set_volume(volume)
        sound.play()
    else:
        print(f"Sound '{name}' not found")


def play_music(name, loops=-1, volume=None):
    global _current_music_name

    if pygame.mixer.music.get_busy() and name == _current_music_name:
        return

    if name in MUSIC:
        if volume is None:
            volume = _current_music_volume

        pygame.mixer.music.load(MUSIC[name])
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)

        _current_music_name = name
    else:
        print(f"Music track '{name}' not found")


def stop_music():
    global _current_music_name
    _current_music_name = None
    pygame.mixer.music.stop()


def set_music_volume(volume):
    global _current_music_volume
    volume = max(0.0, min(1.0, volume))
    _current_music_volume = volume
    pygame.mixer.music.set_volume(volume)


def set_sfx_volume(volume):
    global _current_sfx_volume
    volume = max(0.0, min(1.0, volume))
    _current_sfx_volume = volume
    for sound in SFX.values():
        sound.set_volume(volume)
