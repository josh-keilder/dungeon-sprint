import pygame
from settings import *
from states.dungeons.camera import camera

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)

class FloorTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)
    def draw(self, screen):
        # Draws the tiles based on the camera offset
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y)) 

class WallTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)
    def draw(self, screen):
        # Draws the tiles based on the camera offset
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

class ObjTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)
    def draw(self, screen):
        # Draws the tiles based on the camera offset
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
    