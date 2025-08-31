import pygame
from settings import *
from sprite import Entity
from player import Player


class Scene:
    def __init__(self, app):
        self.app = app

        self.sprites = pygame.sprite.Group()
        self.entity = Entity([self.sprites])

        # Create a player
        self.player = Player([self.sprites])
        
    def update(self):
        # Updates all sprites (Entities and player)
        self.sprites.update()
    def draw(self):
        # Draws our sprites to the screen
        self.sprites.draw(self.app.screen)
        