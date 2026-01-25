import pygame
import globals
from globals import *
from ui_objects.camera import camera
from Components.component import Component

class Hitbox(Component):
    def __init__(self, node):
        super().__init__(node)
        self.mask = pygame.mask.from_surface(node.image)
        self.rect = node.rect.copy()

    def update(self, dt=0):
        # Update Position
        self.rect.topleft = self.node.rect.topleft

        # Updates with animations
        current_image = self.node.image
        self.mask = pygame.mask.from_surface(current_image)

    def collides_with(self, other_hitbox):
        offset = (other_hitbox.rect.x - self.rect.x,
                  other_hitbox.rect.y -self.rect.y)
        return self.mask.overlap(other_hitbox.mask, offset) is not None

    def draw(self, screen, camera=None, color = RED, skip_debug= False):
        # Only draw for debug or specific skip
        if globals.DEBUG_HITBOXES or skip_debug == True:
            outline = self.mask.outline()
            if not outline:
                return  # if mask is empty, skip

            # Create a small surface for the outline
            outline_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            for pixel in outline:
                outline_surf.set_at(pixel, color)
        
            # Draw it at the hitbox's world position based on the entity and camera
            if camera:
                screen.blit(outline_surf, (self.rect.x - camera.x, self.rect.y - camera.y))
            else:
                screen.blit(outline_surf, self.rect.topleft)

        else:
            return
