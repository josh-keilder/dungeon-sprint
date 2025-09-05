import pygame
from settings import *
from button import Button


# Change between screens
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
    def get_state(self):
        return self.currentState
    def set_state(self, state):
        self.currentState = state

# Level screen
class Level:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
    def run(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.gameStateManager.set_state('start')

# Start menu
class Start:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.image = pygame.image.load('Assets/Menu-Assets/start-screen.png').convert_alpha()
        
    def run(self):
        self.display.blit(self.image, (0,0))

class Options:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.image = pygame.image.load('Assets/Menu-Assets/start-screen.png').convert_alpha()
        
    def run(self):
        self.display.blit(self.image, (0,0))


    
