import pygame
from settings import *
from states.dungeons.camera import camera
from Characters.animations import Animations

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos=(0,0), size=TILESIZE, color=(255,0,0)):
        super().__init__(groups)
        # Simple red square
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_frect()
        self.pos = pos
        self.rect.topleft = self.pos

        self.health_bar = self.create_health_bar()

    def update(self, wall_tiles):
        pass

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Display the health bar above the enemy
        self.health_bar_rect.topleft = self.rect.x - camera.x, self.rect.y - camera.y - 10
        screen.blit(self.health_bar, (self.health_bar_rect))

    def patrol(self):
        pass
        # Allows the enemy to patrol from one point to another UNTIL the player is close enough to be spotted
    def attack(self):
        pass
        # Enemy attacks
    def create_health_bar(self):
        # Create a green health bar image
        health_image = pygame.Surface((TILESIZE, 4))
        health_image.fill((0,255,0))
        self.health_bar_rect = health_image.get_frect()

        return health_image
    