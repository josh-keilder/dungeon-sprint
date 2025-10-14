import pygame
import sys
from globals import *
from ui_objects.button import Button
from states.dungeons.dungeon_level_one import Dungeon_Level_One


# Start menu
class Start:
    def __init__(self, screen, gameStateManager, cursor):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.image = START_SCREEN_IMAGE.convert_alpha()
        self.cursor = cursor

        # Create start menu buttons by creating the image and then passing it into the button class 
        self.start_button_img = START_BUTTON_IMAGE.convert_alpha()
        self.start_button =  Button(self.screen, self.start_button_img, pos=(416, 288))
        self.exit_button_img = EXIT_BUTTON_IMAGE.convert_alpha()
        self.exit_button =  Button(self.screen, self.exit_button_img, pos=(416, 448))
        self.options_button_img = OPTIONS_BUTTON_IMAGE.convert_alpha()
        self.options_button =  Button(self.screen, pygame.transform.scale_by(self.options_button_img, 0.5), pos=(985, 650))
        
        # Loads the music and plays it infinitely on the start menu
        try:
            pygame.mixer.music.load("Assets/Music/Starscape.ogg")
        except pygame.error:
            print("Music file not found or could not be loaded.")
        pygame.mixer.music.set_volume(0.01)
        pygame.mixer.music.play(-1)
        
    def draw(self):
        # Draws the background image
        self.screen.blit(self.image, (0,0))
        # Draws the buttons on the start menu
        self.start_button.draw()
        self.exit_button.draw()
        self.options_button.draw()

    def update(self):
        self.start_button.update()
        self.exit_button.update()
        self.options_button.update()
        # If the start button was clicked, it sets the state to the level screen, if the exit button was clicked, it closes the game 
        if self.start_button.is_clicked():
            # Stops the start menu music and creates the dungeon level. Adds it to our states dictionary
            pygame.mixer.music.stop()
            self.dungeon_level_one = Dungeon_Level_One(self.screen, self.gameStateManager, self.cursor)
            self.gameStateManager.add_state('dungeon_level_one', self.dungeon_level_one)
            self.gameStateManager.set_state('dungeon_level_one')

        elif self.options_button.is_clicked():
            self.gameStateManager.set_state('options')

        # Closes the game
        elif self.exit_button.is_clicked():
            pygame.quit()
            sys.exit()