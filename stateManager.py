import pygame
from settings import *


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
        self.display.fill('blue')

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.gameStateManager.set_state('start')
            
            


# Start menu
class Start:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

        
        

    def run(self):
        self.display.fill('red')

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.gameStateManager.set_state('level')
            

    
