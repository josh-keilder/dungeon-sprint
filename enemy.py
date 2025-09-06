import pygame
from settings import *
from sprites import Entity

class Enemy(Entity):
    def __init__(self, groups, image = pygame.Surface((TILESIZE*2, TILESIZE*3)), position = (SCREENWIDTH // 2, SCREENHEIGHT // 2)):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = position)