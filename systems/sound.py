import pygame
import os
from typing import Optional

SFX = {}
MUSIC = {}
_current_sfx_volume = 0.5
_current_music_volume = 0.5


def load_sfx() -> None:
    directory = "Assets/Sounds"
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith((".wav", ".ogg")):
                name = os.path.splitext(file)[0]
                SFX[name] = pygame.mixer.Sound(os.path.join(directory, file))


def load_music() -> None:
    directory = "Assets/Music"
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith((".wav", ".ogg")):
                name = os.path.splitext(file)[0]
                MUSIC[name] = os.path.join(directory, file)


def play_sfx(name: str, volume: Optional[float] = None) -> None:
    if name in SFX:
        sound = SFX[name]
        if volume is None:
            volume = _current_sfx_volume

        sound.set_volume(volume)
        sound.play()
    else:
        print(f"Sound '{name}' not found")


def play_music(
    name: str = None, loops: int = 0, volume: Optional[float] = None
) -> None:
    if pygame.mixer.music.get_busy() and name is None:
        return

    if name in MUSIC:
        if volume is None:
            volume = _current_music_volume

        pygame.mixer.music.load(MUSIC[name])
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
    else:
        print(f"Music track '{name}' not found")


def stop_music() -> None:
    pygame.mixer.music.stop()


def set_music_volume(volume: float) -> None:
    global _current_music_volume
    volume = max(0.0, min(1.0, volume))
    _current_music_volume = volume
    pygame.mixer.music.set_volume(volume)


def set_sfx_volume(volume: float) -> None:
    global _current_sfx_volume
    volume = max(0.0, min(1.0, volume))
    _current_sfx_volume = volume
    for sound in SFX.values():
        sound.set_volume(volume)
