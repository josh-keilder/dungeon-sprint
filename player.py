import pygame
from settings import *
from sprite import Entity

class Player(Entity):
    def __init__(self, groups, image = pygame.Surface((PLAYER_SPRITESIZE, PLAYER_SPRITESIZE)), position = (SCREENWIDTH // 2, SCREENHEIGHT // 2)):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft = position)
        
    def input(self):
        keys = pygame.key.get_pressed()

        # Move left
        if keys[pygame.K_a]:
            self.rect.x -= 1
        # Move right
        if keys[pygame.K_d]:
            self.rect.x += 1
        # Move up
        if keys[pygame.K_w]:
            self.rect.y -= 1
        # Move down
        if keys[pygame.K_s]:
            self.rect.y += 1
    def update(self):
        # Checks for inputs
        self.input()