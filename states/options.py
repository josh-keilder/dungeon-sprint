import pygame
from globals import *

from states.ui_objects.button import Button

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

        self.fps_button_off_img = pygame.transform.scale_by(pygame.image.load('Assets/Menu-Assets/Fps_Off.png').convert_alpha(), 0.5)
        self.fps_button_on_img = pygame.transform.scale_by(pygame.image.load('Assets/Menu-Assets/Fps_On.png').convert_alpha(), 0.5)
        self.fps_button = Button(self.display, self.fps_button_off_img, 450, 200, self.gameStateManager, self.cursor)

        # Toggles
        self.fps_toggle = False

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
            self.fps_button.draw()

            # The back button loads ONLY if the previous state was the gameplay dungeon level
            if self.gameStateManager.get_previous_state().startswith('dungeon_level'):
                  self.back_button.draw()

    def update(self):
        self.main_menu_button.update()

        # Checks for main menu button clicks
        if self.main_menu_button.is_clicked():
            self.gameStateManager.set_state('start')

        # Checks for fps toggle button clicks
        if self.fps_button.is_clicked():
            self.fps_toggle = not self.fps_toggle # Flips toggle
            print(self.fps_toggle)
            if self.fps_toggle == True:
                self.fps_button.image = self.fps_button_on_img
            else:
                self.fps_button.image = self.fps_button_off_img

        
        # If the previous screen was the gameplay dungeon, it also adds a back button to return to the game
        if self.gameStateManager.get_previous_state().startswith('dungeon_level'):
                self.back_button.update()
                if self.back_button.is_clicked():
                    self.gameStateManager.go_back()


        self.fps_button.update()

    def fps_check(self):
         self.fps_check = True

         return self.fps_check
            