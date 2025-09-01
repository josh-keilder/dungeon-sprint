import pygame
from settings import *

from texturedata import solo_texture_data, atlas_texture_data
from sprite import Entity
from player import Player
from textureManager import TextureManager

class Scene:
    def __init__(self, app):
        self.app = app

        self.sprites = pygame.sprite.Group()
        self.entity = Entity([self.sprites])

        # Loads the texture manager module and sets up the solo and atlas texture methods
        self.texture_manager = TextureManager()
        self.solo_textures = self.texture_manager.gen_solo_textures()
        self.atlas_textures = self.texture_manager.gen_atlas_textures('Assets/Proto_Idle_Down.png')

        # Create a player
        self.player = Player([self.sprites], image=self.atlas_textures['player_static'])
        Entity([self.sprites], image=self.atlas_textures['player_static2'])

    def update(self):
        # Updates all sprites (Entities and player)
        self.sprites.update()
    def draw(self):
        # Draws our sprites to the screen
        self.sprites.draw(self.app.screen)
        