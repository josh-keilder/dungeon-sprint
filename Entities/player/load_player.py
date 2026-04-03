"""
Module: Player Loader
---------------------
Handles the initialization and resource management for the Player entity.
This includes:
1. Parsing the Tiled (.tmx) map for the 'Player' spawn object.
2. Slicing and caching player spritesheets.
3. Cropping oversized sprites (64x64) to a standard 16x16 gameplay size.
4. Synchronizing the camera focal point on spawn.
"""

import pygame
from globals import *
from ui_objects.camera import camera_start
from Entities.player.player import Player
from pytmx.util_pygame import load_pygame
from Entities.player.playerTextureData import player_texture_data


def load_player(map) -> object:
    """
    Orchestrates player creation: loads textures, finds spawn point,
    and centers the camera.
    """
    player_textures = gen_player_textures()
    player_pos = get_player_pos(file_path=map.file_path)

    player = Player(animations=player_textures, pos=player_pos, map=map)

    # Snap camera to player immediately to avoid frame-one sliding
    camera_start(player.rect.center)

    return player


def get_player_pos(file_path) -> tuple:
    """
    Scans the Tiled map's Object Layer for an object named 'Player'.
    Returns the (x, y) coordinates for spawning.
    """
    tmx_data = load_pygame(file_path)
    for obj in tmx_data.objects:
        if obj.name == "Player":
            return (obj.x, obj.y)

    # Fallback spawn if no object is found
    return (0, 0)


# Global cache to prevent re-processing textures if the player is re-loaded
_PLAYER_CACHE = None


def gen_player_textures() -> dict:
    """
    Processes player spritesheets into frame lists.

    Includes a specialized cropping step: reduces 64x64 source sprites
    to 16x16 centered frames to ensure the player's collision rect
    matches the visual base of the character.
    """
    global _PLAYER_CACHE
    if _PLAYER_CACHE is not None:
        return _PLAYER_CACHE

    textures = {}

    for name, data in player_texture_data.items():
        player_img = pygame.image.load(data["file_path"]).convert_alpha()
        w, h = data["size"]
        frames = data["frames"]
        row = data["position"][1]

        textures[name] = []

        for i in range(frames):
            # Extract the full sprite frame
            x = i * w
            y = row * h
            frame = player_img.subsurface(pygame.Rect(x, y, w, h))

            # Crop to gameplay size (16x16)
            # This aligns the hitbox to the character's feet/center
            center_x = (w - 16) // 2
            center_y = (h - 16) // 2
            center_rect = pygame.Rect(center_x, center_y, 16, 16)

            # Using .copy() ensures the sub-subsurface isn't tied to the huge original sheet
            cropped_frame = frame.subsurface(center_rect).copy()

            textures[name].append(cropped_frame)

    _PLAYER_CACHE = textures
    return _PLAYER_CACHE
