"""
System: Camera and Display Management
-------------------------------------
Handles the creation of the game window and manages the global camera
state. The camera is used to track targets (like the player) and
determine which objects are currently visible on the screen (culling).

Functions:
    create_screen: Initializes the Pygame display with specific flags.
    camera_start: Sets the initial camera position.
    camera_update: Smoothly or directly centers the camera on a target.
    is_on_screen: Checks if a rectangle is within the camera's view.
    toggle_fullscreen: Switches display modes and updates settings.
"""

import pygame
from globals import SCREENWIDTH, SCREENHEIGHT

# Global camera Rect used by other modules to calculate draw offsets
camera = pygame.Rect(0, 0, SCREENWIDTH, SCREENHEIGHT)


def camera_start(pos):
    """Sets the initial focal point of the camera."""
    camera.center = pos


def camera_update(target):
    """
    Centers the camera on a target.
    Target can be an object with a .rect attribute or a raw (x, y) tuple.
    """
    if hasattr(target, "rect"):
        target_x, target_y = target.rect.center
    else:
        target_x, target_y = target

    camera.center = (target_x, target_y)


def is_on_screen(target_rect):
    """Returns True if the given Rect overlaps with the camera view."""
    return camera.colliderect(target_rect)
