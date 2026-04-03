"""
UI Component: Interactive Button
--------------------------------
Handles basic button functionality including hover detection, visual
outlining, and click event debouncing. Integrated with the SoundController
to provide audio feedback for UI interactions.

Classes:
    Button: A clickable sprite-based UI element.
"""

import pygame
from globals import *
from ui_objects.create_outline import create_outline
from Controllers.sound import SoundController


class Button:
    def __init__(self, screen, image, pos=(0, 0)):
        """
        Initializes the button with an image and position.

        Args:
            screen (pygame.Surface): The surface to draw the button on.
            image (pygame.Surface): The sprite used for the button face.
            pos (tuple): The (x, y) coordinates for the top-left corner.
        """
        self.image = image
        self.rect = self.image.get_frect()
        self.rect.topleft = pos
        self.screen = screen
        self.hovered = False
        self.clicked = False

        self.sound_controller = SoundController()

    def draw(self):
        """Renders the button and its hover outline to the screen."""
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

        if self.hovered:
            create_outline(self.screen, self, WHITE, (self.rect.x, self.rect.y))

    def update(self):
        """Updates the hover state and triggers hover sound effects."""
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if not self.hovered:
                self.sound_controller.play_sfx("Button_Hover")
                self.hovered = True
        else:
            self.hovered = False

    def is_clicked(self) -> bool:
        """
        Detects a single click event (mouse down then up).

        Returns:
            bool: True if the button was clicked in the current frame.
        """
        action = False

        if self.hovered:
            # Check for initial click (button down)
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
                self.sound_controller.play_sfx("Button_Click")

        # Reset 'clicked' state once the mouse button is released
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action
