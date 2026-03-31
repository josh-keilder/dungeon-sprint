import pygame
import globals
from globals import *
from ui_objects.camera import camera
from Components.component import Component

MASK_CACHE = {}


class Hitbox(Component):
    def __init__(self, node):
        super().__init__(node)
        self.rect = node.rect.copy()
        self.mask = self._get_cached_mask(node.image)

    def _get_cached_mask(self, surface):
        # Using the surface object itself as a key is very fast in Python
        if surface not in MASK_CACHE:
            MASK_CACHE[surface] = pygame.mask.from_surface(surface)
        return MASK_CACHE[surface]

    def update(self, dt=0):
        # Update Position
        self.rect.topleft = self.node.rect.topleft

        # Grab the cached mask instead of generating a new one
        self.mask = self._get_cached_mask(self.node.image)

    def collides_with(self, other_hitbox):
        # Standard mask overlap check
        offset = (other_hitbox.rect.x - self.rect.x, other_hitbox.rect.y - self.rect.y)
        return self.mask.overlap(other_hitbox.mask, offset) is not None

    def draw(self, screen, camera=None, color=RED, skip_debug=False):
        # Only draw for debug or specific skip
        if globals.DEBUG_HITBOXES or skip_debug:
            draw_rect = self.rect.copy()
            if camera:
                draw_rect.x -= camera.x
                draw_rect.y -= camera.y

            outline = self.mask.outline()
            for p in outline:
                screen.set_at((int(draw_rect.x + p[0]), int(draw_rect.y + p[1])), color)
