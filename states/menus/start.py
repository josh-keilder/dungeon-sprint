"""
State: Start Menu
-----------------
Manages the initial landing screen of the game. Handles the initialization,
rendering, and interaction logic for menu buttons (Start, Options, Exit)
and initiates the background music for the title screen.

Classes:
    Start: The state object representing the main menu.
"""

import pygame
import sys
from globals import *
from ui_objects.button import Button
from Controllers.sound import SoundController


class Start:
    def __init__(self, screen, gameStateManager, cursor):
        """
        Initializes the start menu, loads assets, and sets up interactive buttons.
        """
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.image = START_SCREEN_IMAGE.convert_alpha()
        self.cursor = cursor

        # Button Initialization
        self.start_button_img = START_BUTTON_IMAGE.convert_alpha()
        self.start_button = Button(self.screen, self.start_button_img, pos=(416, 288))

        self.exit_button_img = EXIT_BUTTON_IMAGE.convert_alpha()
        self.exit_button = Button(self.screen, self.exit_button_img, pos=(416, 448))

        self.options_button_img = OPTIONS_BUTTON_IMAGE.convert_alpha()
        self.options_button = Button(
            self.screen,
            pygame.transform.scale_by(self.options_button_img, 0.5),
            pos=(985, 650),
        )

        # Title Music
        sound_controller = SoundController()
        sound_controller.play_music("JuiceWrldChasingTheDragon")

    def draw(self):
        """Renders the background image and all menu buttons."""
        self.screen.blit(self.image, (0, 0))
        self.start_button.draw()
        self.exit_button.draw()
        self.options_button.draw()

    def update(self, dt):
        """Processes button hover states and handles click-based state transitions."""
        self.start_button.update()
        self.exit_button.update()
        self.options_button.update()

        # Navigation Logic
        if self.start_button.is_clicked():
            self.gameStateManager.set_state("dungeon")

        elif self.options_button.is_clicked():
            self.gameStateManager.set_state("options")

        elif self.exit_button.is_clicked():
            pygame.quit()
            sys.exit()
