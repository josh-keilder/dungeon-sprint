"""
Utility: Visual Effects - Outliner
---------------------------------
Provides a function to generate and render a 1-pixel border around a
sprite's non-transparent pixels. Uses Pygame masks for pixel-perfect
accuracy and implements a caching system to avoid redundant processing.

Functions:
    create_outline: Generates/draws a 4-directional outline around a given object.
"""

import pygame
from globals import *
from ui_objects.camera import camera


def create_outline(screen, object, color, pos, is_camera=False):
    """
    Creates a 1-pixel thick outline around a sprite.

    The outline is cached on the object itself as 'cached_outline_surf'
    to prevent expensive mask calculations on every frame.

    Args:
        screen (pygame.Surface): The surface to draw onto.
        object (Sprite/Node): The object containing the .image to outline.
        color (tuple): RGB(A) color for the outline.
        pos (tuple): The (x, y) coordinates to draw the outline.
        is_camera (bool): If True, adjusts coordinates based on global camera offset.
    """

    # Cache Check: Only generate the mask surface if it doesn't exist yet
    if not hasattr(object, "cached_outline_surf"):
        object_image = object.image
        mask = pygame.mask.from_surface(object_image)
        mask_outline = mask.outline()

        # Create an empty transparent surface the same size as the sprite
        mask_surf = pygame.Surface(object_image.get_size(), pygame.SRCALPHA)
        for pixel in mask_outline:
            mask_surf.set_at(pixel, color)

        # Ensure black pixels don't interfere with transparency
        mask_surf.set_colorkey((0, 0, 0))
        object.cached_outline_surf = mask_surf

    outline_to_draw = object.cached_outline_surf

    # Coordinate Calculation: Handle screen-space vs world-space (camera)
    if not is_camera:
        draw_pos = pos
    else:
        draw_pos = (pos[0] - camera.x, pos[1] - camera.y)

    # Render the outline by blitting the mask surface in 4 directions
    # (Left, Right, Up, Down) to create a solid border.
    screen.blit(outline_to_draw, (draw_pos[0] - 1, draw_pos[1]))
    screen.blit(outline_to_draw, (draw_pos[0] + 1, draw_pos[1]))
    screen.blit(outline_to_draw, (draw_pos[0], draw_pos[1] - 1))
    screen.blit(outline_to_draw, (draw_pos[0], draw_pos[1] + 1))
