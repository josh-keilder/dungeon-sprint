import pygame

from globals import SCREENHEIGHT, SCREENWIDTH

camera = pygame.Rect(0, 0, SCREENWIDTH, SCREENHEIGHT)


def center_camera(pos):
    camera.center = pos


def is_on_screen(target_rect):
    return camera.colliderect(target_rect)
