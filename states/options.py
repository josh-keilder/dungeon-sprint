import pygame
from globals import *

from states.button import Button

class Options:
    def __init__(self, display, gameStateManager, cursor):
        self.display = display
        self.gameStateManager = gameStateManager
        self.cursor = cursor
        self.image = pygame.image.load('Assets/Menu-Assets/options-screen.png').convert_alpha()

        # Create option menu buttons
        self.main_menu_img_button = pygame.image.load('Assets/Menu-Assets/main-menu-button.png').convert_alpha()
        self.main_menu_button =  Button(self.display, pygame.transform.scale_by(self.main_menu_img_button, 0.4), 15, 650, self.gameStateManager, self.cursor)
        self.back_img_button = pygame.image.load('Assets/Menu-Assets/back-button.png').convert_alpha()
        self.back_button =  Button(self.display, pygame.transform.scale_by(self.back_img_button, 0.4), 1135, 650, self.gameStateManager, self.cursor)

        # Loads unpausing sound
        try:
            self.unpause_sound = pygame.mixer.Sound("Assets/Sounds/Pause.wav")
        except Exception:
            self.unpause_sound = None
        
    def draw(self):
        self.display.blit(self.image, (0,0))
        # Draws the buttons on the options menu
        if self.gameStateManager.currentState == 'options':
             self.main_menu_button.draw()
             # The back button loads ONLY if the previous state was the gameplay dungeon level
             if self.gameStateManager.get_previous_state().startswith('dungeon_level'):
                  self.back_button.draw()

    def update(self):
        self.main_menu_button.update()
        # Checks for button clicks
        if self.main_menu_button.is_clicked():
            self.gameStateManager.set_state('start')
        # If the previous screen was the gameplay dungeon, it also adds a back button to return to the game
        if self.gameStateManager.get_previous_state().startswith('dungeon_level'):
                self.back_button.update()
                if self.back_button.is_clicked():
                    self.gameStateManager.go_back()
            