import pygame
import sys

from settings import *
from player import *
from scene import Scene
from stateManager import Level, Start, GameStateManager
from button import Button

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Dungeon Sprint")

        self.running = True

        # Allows the game to change from different states(menus/levels) and automatically sets it to our start screen first
        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager)
        self.level = Level(self.screen, self.gameStateManager)

        # A dictionary to keep track of the states and their ids
        self.states = {'start':self.start, 'level':self.level}

        # Initialize our game scene
        self.scene = Scene(self)

    def run(self):
            while self.running:
                 self.update()
                 self.draw()
            self.close()
    def update(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

        # Updates the scene
        self.scene.update()

        pygame.display.update()
        self.clock.tick(FRAMERATE)
    def draw(self):
        # inside of the self.states dictionary, look for the key that is returned from the get_state() method and update it
        self.states[self.gameStateManager.get_state()].run()

        if self.gameStateManager.currentState == 'start':
            # Create start menu buttons
            self.start_button_img = pygame.image.load('Assets/Menu-Assets/start-button.png').convert_alpha()
            self.exit_button_img = pygame.image.load('Assets/Menu-Assets/exit-button.png').convert_alpha()
            # Display the buttons
            self.start_button =  Button(self.screen, self.start_button_img, 416, 288)
            self.exit_button =  Button(self.screen, self.exit_button_img, 416, 448)

            # If the start button was clicked, it sets the state to the level screen, if the exit button was clicked, it closes the game 
            if self.start_button.draw():
                 self.gameStateManager.set_state('level')
            elif self.exit_button.draw():
                self.close()

        # If the current state is our level state, it draws the scene
        if self.gameStateManager.currentState == 'level':
            self.scene.draw()
    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()

