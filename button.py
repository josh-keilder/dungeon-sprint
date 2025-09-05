import pygame
from settings import *

class Button():
    def __init__(self, screen, image, pos_x, pos_y):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos_x,pos_y)
        self.screen = screen
        self.clicked = False

    def draw(self):
        # gets mouse position
        pos = pygame.mouse.get_pos()
        action = False
        # checks if mouse is over and clicked the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
                print('Button clicked')        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # puts the buttons on screen at the rect topleft coordinates
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

        return action
