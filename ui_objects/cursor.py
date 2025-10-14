import pygame
from globals import *

class Cursor:
    def __init__(self, screen, image):
        self.screen = screen
        self.image = image
        self.rect =  self.image.get_frect()

    def set_image(self, new_image):
        self.image = new_image
        self.rect = self.image.get_frect(center=self.rect.center)

    def update(self):
        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
        self.rect.center = mouse_pos_x + 5, mouse_pos_y + 5

    def draw(self):
        self.screen.blit(self.image, self.rect)

    