import pygame
import sys

from settings import *
from stateManager import Dungeon_Level, Start, GameStateManager
from button import Button
from camera import create_screen

class Game:
    def __init__(self):
        pygame.init()
        # The screen is created within the camera module to allow a player following camera
        self.screen = create_screen(SCREENWIDTH, SCREENHEIGHT, "Dungeon Sprint")
        self.clock = pygame.time.Clock()
        self.running = True

        self.sprites = pygame.sprite.Group()

        # Allows the game to change from different states(menus/levels) and automatically sets it to our start screen first
        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager)
        self.dungeon_level = None

        # A dictionary to keep track of the states and their ids (Only loads start menu at first)
        self.states = {'start':self.start}

        # Create start menu buttons by creating the image and then passing it into the button class
        self.start_button_img = pygame.image.load('Assets/Menu-Assets/start-button.png').convert_alpha()
        self.exit_button_img = pygame.image.load('Assets/Menu-Assets/exit-button.png').convert_alpha()
        self.start_button =  Button(self.screen, self.start_button_img, 416, 288)
        self.exit_button =  Button(self.screen, self.exit_button_img, 416, 448)

    def run(self):
            while self.running:
                 self.update()
                 self.draw()
            self.close()

    def update(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

        # Updates current state
        self.states[self.gameStateManager.get_state()].update()

        if self.gameStateManager.currentState == 'start':
            # If the start button was clicked, it sets the state to the level screen, if the exit button was clicked, it closes the game 
            if self.start_button.is_clicked():
                # Stops the start menu music and creates the dungeon level. Adds it to our states dictionary
                pygame.mixer.music.stop()
                self.dungeon_level = Dungeon_Level(self.screen, self.gameStateManager)
                self.states['dungeon_level'] = self.dungeon_level
                self.gameStateManager.set_state('dungeon_level')
            elif self.exit_button.is_clicked():
                 self.close()

        pygame.display.update()
        self.clock.tick(FRAMERATE)

    def draw(self):
        # Clears the screen so theres no duplicate sprites
        self.screen.fill(CLEAR)

        # Inside of the self.states dictionary, look for the key that is returned from the get_state() method and update it
        self.states[self.gameStateManager.get_state()].draw()

        # Draws the buttons on the start menu
        if self.gameStateManager.currentState == 'start':
            self.start_button.draw()
            self.exit_button.draw()

    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()