import pygame
from settings import *

from player import Player
from map_loader import MapLoader

# Change between screens
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
    def get_state(self):
        return self.currentState
    def set_state(self, state):
        self.currentState = state

# Dungeon_Level screen
class Dungeon_Level:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        self.sprites = pygame.sprite.Group()

        # Loads our tmx map file
        self.tilemap_dungeon = MapLoader.load_map(self, file_path = "Assets/Maps/Dungeon Room.tmx")

        # Loads the player
        self.player_textures = Player.gen_player_textures(self)
        self.player = Player([self.sprites], animations=self.player_textures)

    def run(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.gameStateManager.set_state('start')

    def update(self):
        # Updates all sprites (Entities and player)
        self.sprites.update()
    def draw(self):
        # Draws our sprites to the screen 
        self.sprites.draw(self.display)
        
# Start menu
class Start:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.image = pygame.image.load('Assets/Menu-Assets/start-screen.png').convert_alpha()
        
    def run(self):
        self.display.blit(self.image, (0,0))
    def update(self):
        pass

class Options:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.image = pygame.image.load('Assets/Menu-Assets/start-screen.png').convert_alpha()
        
    def run(self):
        self.display.blit(self.image, (0,0))


    
