import pygame
import sys

from settings import *
from states.stateManager import GameStateManager

from states.dungeons.dungeon_level_one import Dungeon_Level_One
from states.start import Start
from states.options import Options
from states.button import Button
from camera import create_screen

class Game:
    def __init__(self):
        pygame.init()
        # The screen is created within the camera module to allow a player following camera
        self.screen = create_screen(SCREENWIDTH, SCREENHEIGHT, "Dungeon Sprint")
        self.clock = pygame.time.Clock()
        self.running = True

        

        # Allows the game to change from different states(menus/levels) and automatically sets it to our start screen first
        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager)
        self.options = Options(self.screen, self.gameStateManager)
        self.dungeon_level = None

        # A dictionary to keep track of the states and their ids (Only loads start menu at first)
        self.states = {'start':self.start, 'options':self.options}

        # Create start menu buttons by creating the image and then passing it into the button class 
        self.start_button_img = pygame.image.load('Assets/Menu-Assets/start-button.png').convert_alpha()
        self.start_button =  Button(self.screen, self.start_button_img, 416, 288)
        self.exit_button_img = pygame.image.load('Assets/Menu-Assets/exit-button.png').convert_alpha()
        self.exit_button =  Button(self.screen, self.exit_button_img, 416, 448)
        self.options_button_img = pygame.image.load('Assets/Menu-Assets/options-button.png').convert_alpha()
        self.options_button =  Button(self.screen, pygame.transform.scale_by(self.options_button_img, 0.5), 985, 650)

        # Create option menu buttons
        self.main_menu_img_button = pygame.image.load('Assets/Menu-Assets/main-menu-button.png').convert_alpha()
        self.main_menu_button =  Button(self.screen, pygame.transform.scale_by(self.main_menu_img_button, 0.4), 15, 650)
        self.back_img_button = pygame.image.load('Assets/Menu-Assets/back-button.png').convert_alpha()
        self.back_button =  Button(self.screen, pygame.transform.scale_by(self.back_img_button, 0.4), 1135, 650)

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
                self.dungeon_level_one = Dungeon_Level_One(self.screen, self.gameStateManager)
                self.states['dungeon_level_one'] = self.dungeon_level_one
                self.gameStateManager.set_state('dungeon_level_one')

            elif self.options_button.is_clicked():
                self.gameStateManager.set_state('options')

            # Closes the game
            elif self.exit_button.is_clicked():
                self.close()

        # Sets the options screen
        elif self.gameStateManager.currentState == 'options':
            if self.main_menu_button.is_clicked():
                self.gameStateManager.set_state('start')
            # If the previous screen was the gameplay dungeon, it also adds a back button to return to the game
            if self.gameStateManager.get_previous_state().startswith('dungeon_level'):
                 if self.back_button.is_clicked():
                      self.gameStateManager.go_back()

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
            self.options_button.draw()
            # Draws the buttons on the options menu
        elif self.gameStateManager.currentState == 'options':
             self.main_menu_button.draw()
             # The back button loads ONLY if the previous state was the gameplay dungeon level
             if self.gameStateManager.get_previous_state().startswith('dungeon_level'):
                  self.back_button.draw()

    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()