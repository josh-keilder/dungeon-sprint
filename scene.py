import pygame
from settings import *

from sprite import Entity, TileEntity
from player import Player
from textureManager import TextureManager
from map_loader import MapLoader

class Scene:
    def __init__(self, app):
        self.app = app

        self.sprites = pygame.sprite.LayeredUpdates()
        self.entity = Entity([self.sprites])

        # reads the csv file for each layer
        self.tilemap_dungeon_layer_1 = MapLoader.load_csv_map(self, file_path = "Assets/Dungeon-Layers/test-dungeon-2-tile-layer-1.csv")
        self.tilemap_dungeon_layer_2 = MapLoader.load_csv_map(self, file_path = "Assets/Dungeon-Layers/test-dungeon-2-tile-layer-2.csv")

        # Loads the texture manager module and sets up the solo and atlas texture methods
        self.texture_manager = TextureManager()
        self.solo_textures = self.texture_manager.gen_solo_textures()
        self.atlas_textures = self.texture_manager.gen_atlas_textures('Assets/Dungeon_Tileset.png')

        # Loads the player
        self.player_textures = self.texture_manager.gen_player_textures()
        self.player = Player([self.sprites], animations=self.player_textures)
        self.sprites.change_layer(self.player, 2)
        # Entity([self.sprites], image=self.atlas_textures['top_wall'])

        # load the tiles
        self.create_tiles = MapLoader.create_tiles(self, self.tilemap_dungeon_layer_1, 0)
        self.create_tiles = MapLoader.create_tiles(self, self.tilemap_dungeon_layer_2, 1)

    def update(self):
        # Updates all sprites (Entities and player)
        self.sprites.update()



    def draw(self):
        # Draws our sprites to the screen 
        self.sprites.draw(self.app.screen)

                   
    
        