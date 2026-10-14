import pygame

from globals import SCREEN_HEIGHT, SCREEN_WIDTH

camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


def center_camera(pos):
    camera.center = pos


def is_on_screen(target_rect):
    return camera.colliderect(target_rect)
