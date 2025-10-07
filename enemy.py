import pygame
from settings import *
from camera import camera
from animations import Animations

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos=(0,0), size=TILESIZE, color=(255,0,0)):
        super().__init__(groups)
        # Simple red square
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_frect()
        self.rect.topleft = pos

    def update(self, wall_tiles):
        pass

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

    def patrol(self):
        pass
        # Allows the enemy to patrol from one point to another UNTIL the player is close enough to be spotted
    def attack(self):
        pass
        # Enemy attacks
    