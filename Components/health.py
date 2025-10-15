import pygame
from globals import *

class Health:
    def __init__(self, max_health):
        self.max_health = max_health
        self.current = max_health

    def take_damage(self, amount):
        self.current = max(0, self.current - amount)
    
    def heal(self, amount):
        self.current = min(self.max_health, self.current + amount)
        
    def is_dead(self):
        return self.current <= 0
    
    def display_health_bar():
        # Create a green health bar image
        health_image = pygame.Surface((TILESIZE, 4))
        health_image.fill(GREEN)
        health_bar_rect = health_image.get_frect()

        return health_image, health_bar_rect
    