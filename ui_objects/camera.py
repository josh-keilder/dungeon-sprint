import pygame
from globals import *
from settings_manager import SettingsManager

settings_manager = SettingsManager()

camera = pygame.Rect(0, 0, 0, 0)


def create_screen(width, height, title):
    pygame.display.set_caption(title)

    flags = pygame.SCALED

    if settings_manager.get("full_screen_enabled"):
        flags |= pygame.FULLSCREEN
    
    screen = pygame.display.set_mode((width, height), flags)

    camera.width = width
    camera.height = height
    return screen


def camera_start(pos):
    camera.center = pos


def camera_update(target):
    # Center the camera on the target (sprite or (x,y)) each frame
    if hasattr(target, "rect"):
        target_x, target_y = target.rect.center
    else:
        target_x, target_y = target
    camera.center = (target_x, target_y)


def is_on_screen(target_rect):
    return camera.colliderect(target_rect)


def toggle_fullscreen():
    current = settings_manager.get("full_screen_enabled")
    settings_manager.set("full_screen_enabled", not current)
    
    return create_screen(SCREENWIDTH, SCREENHEIGHT, "Dungeon Sprint")