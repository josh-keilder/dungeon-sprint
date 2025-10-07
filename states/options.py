import pygame
from settings import *

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
            