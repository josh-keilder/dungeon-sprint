import pygame
from settings import *

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)

class FloorTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)

class WallTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)

class ObjTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)