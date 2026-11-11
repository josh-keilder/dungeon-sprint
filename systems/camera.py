import pygame

from globals import WORLD_HEIGHT, WORLD_WIDTH

camera = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)


def center_camera(pos):
    camera.center = pos


def is_on_screen(target_rect):
    return camera.colliderect(target_rect)
