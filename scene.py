import pygame
from settings import *

from player import Player
from map_loader import MapLoader

class Scene:
    def __init__(self, app):
        self.app = app

        # Initialize our sprite group
        self.sprites = pygame.sprite.Group()

        # Loads our tmx map file
        self.tilemap_dungeon = MapLoader.load_map(self, file_path = "Assets/Maps/Dungeon Room.tmx")

        # Loads the player
        self.player_textures = Player.gen_player_textures(self)
        self.player = Player([self.sprites], animations=self.player_textures)

    def update(self):
        # Updates all sprites (Entities and player)
        self.sprites.update()



    def draw(self):
        # Draws our sprites to the screen 
        self.sprites.draw(self.app.screen)

                   
    
        