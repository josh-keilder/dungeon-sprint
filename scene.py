import pygame
from settings import *

from sprite import Entity, TileEntity
from player import Player
from textureManager import TextureManager
import csv

class Scene:
    def __init__(self, app):
        self.app = app

        self.sprites = pygame.sprite.LayeredUpdates()
        self.entity = Entity([self.sprites])

        self.tilemap = self.load_csv_map("Assets/test-dungeon-1_Tile Layer 1.csv")
        # Loads the texture manager module and sets up the solo and atlas texture methods
        self.texture_manager = TextureManager()
        self.solo_textures = self.texture_manager.gen_solo_textures()
        self.atlas_textures = self.texture_manager.gen_atlas_textures('Assets/Dungeon_Tileset.png')
        # load the tiles
        self.create_tiles()

        # Create a player
        self.player_textures = self.texture_manager.gen_player_textures('Assets/Proto_Idle_Down.png')
        self.player = Player([self.sprites], image=self.player_textures['player'])
        self.sprites.change_layer(self.player, 1)
        # Entity([self.sprites], image=self.atlas_textures['top_wall'])

        # load the tiles
        self.create_tiles()

    def update(self):
        # Updates all sprites (Entities and player)
        self.sprites.update()
    def draw(self):
        # Draws our sprites to the screen 
        self.sprites.draw(self.app.screen)
    # Reads the map csv and returns it as a list
    def load_csv_map(self, file_path):
        with open(file_path) as file:
            reader = csv.reader(file)
            return [[int(cell) for cell in row] for row in reader]
    # Takes the tilemap and makes tile entities
    def create_tiles(self):
        for row_index, row in enumerate(self.tilemap):
            for col_index, tile in enumerate(row):
                if tile != -1:
                    image = self.atlas_textures[tile]
                    tile_entity = TileEntity([self.sprites], image, position = (col_index * TILESIZE, row_index * TILESIZE))
                    self.sprites.change_layer(tile_entity,0)
                   
    
        