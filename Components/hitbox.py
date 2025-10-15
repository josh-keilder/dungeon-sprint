import pygame
from globals import *
from ui_objects.camera import camera

class Hitbox:
    def __init__(self, entity):
        self.entity = entity
        self.mask = pygame.mask.from_surface(entity.image)
        self.rect = entity.rect.copy()

    def update(self):
        # Update Position
        self.rect.topleft = self.entity.rect.topleft

        # Updates with animations
        current_image = self.entity.image
        self.mask = pygame.mask.from_surface(current_image)

    def collides_with(self, other_hitbox):
        offset = (other_hitbox.rect.x - self.rect.x,
                  other_hitbox.rect.y -self.rect.y)
        return self.mask.overlap(other_hitbox.mask, offset) is not None

    def draw(self, screen, color = (255, 0, 0)):
        outline = self.mask.outline()
        if not outline:
            return  # if mask is empty, skip

        # Create a small surface for the outline
        outline_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for pixel in outline:
            outline_surf.set_at(pixel, color)
        
        # Draw it at the hitbox's world position based on the entity and camera
        screen.blit(outline_surf, (self.rect.x - camera.x, self.rect.y - camera.y))
