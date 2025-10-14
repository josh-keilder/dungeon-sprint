import pygame
from globals import *

class Text_Loader:
    def __init__(self, text, screen, font_name = 'Comic Sans MS', font_size=30, color= BLACK, pos=(0,0)):
        pygame.font.init()
        self.font = pygame.font.SysFont(font_name, font_size)
        self.screen = screen
        self.color = color
        self.pos = pos
        self.text = text
        self.text_surface = self.font.render(self.text, False, self.color)

    def draw(self):
        self.screen.blit(self.text_surface, self.pos)

    def update_text(self, new_text):
        self.text_surface = self.font.render(new_text, False, self.color)