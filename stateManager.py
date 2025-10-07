import pygame
from settings import *

from player import Player
from map_loader import MapLoader
from camera import camera_start, camera_update

pygame.mixer.init()

# Change between screens
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
        self.state_history = []
    def get_state(self):
        return self.currentState
    def set_state(self, new_state):
        if self.currentState:
            self.state_history.append(self.currentState)
        self.currentState = new_state
    def get_previous_state(self):
        # If history is available, return the previous one
        if self.state_history:
            return self.state_history[-1]
        return None
    def go_back(self):
        # Pop the last state if available
        if self.state_history:
            self.currentState = self.state_history.pop()


# Dungeon_Level screen
class Dungeon_Level:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        pygame.mixer.music.stop() # Automatically stops the start menu music

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

        # Load the pause sound and pause cooldown
        try:
            self.pause_sound = pygame.mixer.Sound("Assets/Sounds/Pause.wav")
        except Exception:
            self.pause_sound = None

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.gameStateManager.set_state('options')
            self.pause_sound.play()

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
        # for wall in self.wall_tiles:
        #     pygame.draw.rect(self.display, (255,0,0), wall.rect, 2)
        # pygame.draw.rect(self.display, (0,255,0), self.player.rect, 2)
        
# Start menu
class Start:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.image = pygame.image.load('Assets/Menu-Assets/start-screen.png').convert_alpha()
        
        # Loads the music and plays it infinitely on the start menu
        try:
            pygame.mixer.music.load("Assets/Music/Starscape.ogg")
        except pygame.error:
            print("Music file not found or could not be loaded.")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)
        
    def draw(self):
        self.display.blit(self.image, (0,0))
    def update(self):
        pass

class Options:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.image = pygame.image.load('Assets/Menu-Assets/options-screen.png').convert_alpha()

        # Loads unpausing sound
        try:
            self.unpause_sound = pygame.mixer.Sound("Assets/Sounds/Pause.wav")
        except Exception:
            self.unpause_sound = None
        
    def draw(self):
        self.display.blit(self.image, (0,0))

    def update(self):
        pass
            
            


    
