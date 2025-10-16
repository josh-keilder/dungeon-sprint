import pygame
from globals import *
from ui_objects.camera import camera
from Components.hitbox import Hitbox

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

        # Hitbox
        self.hitbox = Hitbox(self)

    def update(self):
        # Hitbox
        self.hitbox.update()

    def draw(self, screen):
        # Draws the tiles based on the camera offset
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Show Hitbox for debug
        self.hitbox.draw(screen, color=BLUE)

class ObjTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)
    def draw(self, screen):
        # Draws the tiles based on the camera offset
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
    