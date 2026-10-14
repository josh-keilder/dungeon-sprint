import pygame

from globals import SCREENHEIGHT, SCREENWIDTH

camera = pygame.Rect(0, 0, SCREENWIDTH, SCREENHEIGHT)


def center_camera(pos):
    camera.center = pos


def is_on_screen(target_rect):
    """Returns True if the given Rect overlaps with the camera view."""
    return camera.colliderect(target_rect)
