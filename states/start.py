import pygame
from settings import *

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
        pygame.mixer.music.set_volume(0.01)
        pygame.mixer.music.play(-1)
        
    def draw(self):
        self.display.blit(self.image, (0,0))
    def update(self):
        pass