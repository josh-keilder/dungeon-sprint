import pygame
from settings import *

from player import Player
from map_loader import MapLoader
from camera import camera_start, camera_update

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
        self.wall_tiles = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()

        # Loads our tmx map file
        self.tilemap_dungeon = MapLoader.load_map(self, self.sprites, self.wall_tiles, file_path = "Assets/Maps/Dungeon Room.tmx")

        # Loads the player
        self.player_textures = Player.gen_player_textures(self)
        self.player_pos = MapLoader.get_player_pos(self, file_path = "Assets/Maps/Dungeon Room.tmx")
        self.player = Player([self.player_group], animations=self.player_textures, pos = self.player_pos)

        camera_start(self.player.rect.center)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.gameStateManager.set_state('start')
            
        # Updates all sprites (Entities and player)
        self.player.update(self.wall_tiles) # Passes the wall tiles into the player update to test for collisions
        self.sprites.update()
        self.wall_tiles.update()

        camera_update(self.player)

    def draw(self):
        # Draws our sprites and walls to the screen 
        for sprite in self.sprites:
            sprite.draw(self.display)
        for wall in self.wall_tiles:
            wall.draw(self.display)

        if self.player_group.sprite:
           self.player_group.sprite.draw(self.display)

        # Shows the wall hitboxes and player hitboxes for collision detection
        for wall in self.wall_tiles:
            pygame.draw.rect(self.display, (255,0,0), wall.rect, 2)
        pygame.draw.rect(self.display, (0,255,0), self.player.rect, 2)
        
# Start menu
class Start:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.image = pygame.image.load('Assets/Menu-Assets/start-screen.png').convert_alpha()
        
    def draw(self):
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


    
