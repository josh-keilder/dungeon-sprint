import pygame
from globals import * 

camera = pygame.Rect(0, 0, 0, 0)

def create_screen(width, height, title):
    pygame.display.set_caption(title)
    screen = pygame.display.set_mode((width, height))
    camera.width = width
    camera.height = height
    return screen

def camera_start(pos):
    camera.center = pos

def camera_update(target):
    # Center the camera on the target (sprite or (x,y)) each frame
    if hasattr(target, 'rect'):
        target_x, target_y = target.rect.center
    else:
        target_x, target_y = target
    camera.center = (target_x, target_y)