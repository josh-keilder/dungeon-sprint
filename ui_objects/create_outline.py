import pygame
from globals import *

def create_outline(screen, object, color, pos):
    object_image = object.image
    mask = pygame.mask.from_surface(object_image)
    mask_outline = mask.outline()
    mask_surf = pygame.Surface(object_image.get_size())
    for pixel in mask_outline:
        mask_surf.set_at(pixel,(color))
    mask_surf.set_colorkey((0,0,0))
    screen.blit(mask_surf,(pos[0] - 1, pos[1]))
    screen.blit(mask_surf,(pos[0] + 1, pos[1]))
    screen.blit(mask_surf,(pos[0], pos[1] - 1))
    screen.blit(mask_surf,(pos[0], pos[1] + 1))