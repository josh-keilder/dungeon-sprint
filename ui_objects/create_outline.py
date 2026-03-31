import pygame
from globals import *
from ui_objects.camera import camera


def create_outline(screen, object, color, pos, is_camera=False):
    if not hasattr(object, "cached_outline_surf"):
        object_image = object.image
        mask = pygame.mask.from_surface(object_image)
        mask_outline = mask.outline()

        mask_surf = pygame.Surface(object_image.get_size(), pygame.SRCALPHA)
        for pixel in mask_outline:
            mask_surf.set_at(pixel, color)
        mask_surf.set_colorkey((0, 0, 0))

        object.cached_outline_surf = mask_surf

    outline_to_draw = object.cached_outline_surf

    if not is_camera:
        draw_pos = pos
    else:
        draw_pos = (pos[0] - camera.x, pos[1] - camera.y)

    screen.blit(outline_to_draw, (draw_pos[0] - 1, draw_pos[1]))
    screen.blit(outline_to_draw, (draw_pos[0] + 1, draw_pos[1]))
    screen.blit(outline_to_draw, (draw_pos[0], draw_pos[1] - 1))
    screen.blit(outline_to_draw, (draw_pos[0], draw_pos[1] + 1))
