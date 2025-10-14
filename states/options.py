import pygame
from globals import *

from ui_objects.button import Button

class Options:
    def __init__(self, screen, gameStateManager, cursor):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.cursor = cursor
        self.image = OPTIONS_SCREEN_IMAGE.convert_alpha()

        # Create option menu buttons
        self.main_menu_button_img = MAIN_MENU_BUTTON_IMAGE.convert_alpha()
        self.main_menu_button =  Button(self.screen, pygame.transform.scale_by(self.main_menu_button_img, 0.4), pos=(15, 650))
        self.back_button_img = BACK_BUTTON_IMAGE.convert_alpha()
        self.back_button =  Button(self.screen, pygame.transform.scale_by(self.back_button_img, 0.4), pos=(1135, 650))

        self.fps_button_off_img = pygame.transform.scale_by(FPS_BUTTON_OFF_IMAGE.convert_alpha(), 0.5)
        self.fps_button_on_img = pygame.transform.scale_by(FPS_BUTTON_ON_IMAGE.convert_alpha(), 0.5)
        self.fps_button = Button(self.screen, self.fps_button_off_img, pos=(450, 200))

        # Toggles
        self.fps_toggle = False

        # Loads unpausing sound
        try:
            self.unpause_sound = pygame.mixer.Sound("Assets/Sounds/Pause.wav")
        except Exception:
            self.unpause_sound = None
        
    def draw(self):
        self.screen.blit(self.image, (0,0))

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
            