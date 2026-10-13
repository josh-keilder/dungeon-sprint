import pygame
from globals import *
from ui_objects.button import Button


class Start:
    def __init__(self, gameStateManager):
        """
        Initializes the start menu, loads assets, and sets up interactive buttons.
        """
        self.gameStateManager = gameStateManager
        self.image = START_SCREEN_IMAGE.convert_alpha()

        # Button Initialization
        self.start_button_img = START_BUTTON_IMAGE.convert_alpha()
        self.start_button = Button(self.start_button_img, pos=(416, 288))

        self.exit_button_img = EXIT_BUTTON_IMAGE.convert_alpha()
        self.exit_button = Button(self.exit_button_img, pos=(416, 448))

        self.options_button_img = OPTIONS_BUTTON_IMAGE.convert_alpha()
        self.options_button = Button(
            pygame.transform.scale_by(self.options_button_img, 0.5),
            pos=(985, 650),
        )

    def draw(self, screen):
        """Renders the background image and all menu buttons."""
        screen.blit(self.image, (0, 0))
        self.start_button.draw(screen)
        self.exit_button.draw(screen)
        self.options_button.draw(screen)

    def update(self, dt):
        """Processes button hover states and handles click-based state transitions."""
        self.start_button.update()
        self.exit_button.update()
        self.options_button.update()

        # Navigation Logic
        if self.start_button.is_clicked():
            self.gameStateManager.set_state("level")

        elif self.options_button.is_clicked():
            self.gameStateManager.set_state("options")

        elif self.exit_button.is_clicked():
            pygame.event.post(pygame.event.Event(pygame.QUIT))
