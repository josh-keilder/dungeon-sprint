import pygame
from globals import *

class Cursor:
    def __init__(self, screen, image):
        self.screen = screen
        self.image = image
        self.rect =  self.image.get_frect()
        self.default_image = image

    def set_image(self, new_image):
        self.image = new_image
        self.rect = self.image.get_frect(center=self.rect.center)

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

    def draw(self):
        self.screen.blit(self.image, self.rect)

    