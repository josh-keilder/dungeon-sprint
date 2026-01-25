import pygame
from globals import *
from ui_objects.camera import camera

def create_outline(screen, object, color, pos, is_camera = False):
    object_image = object.image
    mask = pygame.mask.from_surface(object_image)
    mask_outline = mask.outline()
    mask_surf = pygame.Surface(object_image.get_size(), pygame.SRCALPHA)
    for pixel in mask_outline:
        mask_surf.set_at(pixel,(color))
    mask_surf.set_colorkey((0,0,0))

    if not is_camera:
        screen.blit(mask_surf,(pos[0] - 1, pos[1]))
        screen.blit(mask_surf,(pos[0] + 1, pos[1]))
        screen.blit(mask_surf,(pos[0], pos[1] - 1))
        screen.blit(mask_surf,(pos[0], pos[1] + 1))
    else:
        # Apply camera offset
        offset_pos = (pos[0] - camera.x, pos[1] - camera.y)
        screen.blit(mask_surf, (offset_pos[0] - 1, offset_pos[1]))
        screen.blit(mask_surf, (offset_pos[0] + 1, offset_pos[1]))
        screen.blit(mask_surf, (offset_pos[0], offset_pos[1] - 1))
        screen.blit(mask_surf, (offset_pos[0], offset_pos[1] + 1))