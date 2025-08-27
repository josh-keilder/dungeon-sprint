import pygame


class Player:
    def __init__(self, x , y, color):
        self.x = x
        self.y = y
        self.color = color
    
    
    def render(self):
        pygame.draw.rect(self.screen, self.color, (self.x, self.y))
        
    def up(self):
        self.y = self.y - self.speed
        
    def down(self):
        self.y = self.y + self.speed
        
    def left(self):
        self.x = self.x - self.speed
        
    def right(self):
        self.x = self.x + self.speed
