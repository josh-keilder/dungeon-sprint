"""
UI Component: Custom Cursor
---------------------------
Replaces the standard system mouse pointer with a custom sprite. Handles
positional updates based on mouse hardware input and allows for dynamic
image swapping (e.g., changing to a "hand" icon on hover).

Classes:
    Cursor: Manages the rendering and positioning of the custom cursor sprite.
"""

import pygame
from globals import *


class Cursor:
    def __init__(self, screen, image):
        """
        Initializes the cursor with a specific image and a floating-point rect.

        Args:
            screen (pygame.Surface): The main display surface.
            image (pygame.Surface): The sprite to use as the cursor.
        """
        self.screen = screen
        self.image = image
        # Using frect (float rect) for sub-pixel precision and smoother movement
        self.rect = self.image.get_frect()

    def set_image(self, new_image):
        """Updates the cursor sprite while maintaining the current center position."""
        self.image = new_image
        self.rect = self.image.get_frect(center=self.rect.center)

    def update(self):
        """Syncs the cursor position with the system mouse coordinates."""
        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()

        # Slight offset (+5) to prevent the cursor point from being directly
        # under the top-left pixel, improving visual feel.
        self.rect.center = mouse_pos_x + 5, mouse_pos_y + 5

    def draw(self):
        """Draws the cursor to the screen."""
        self.screen.blit(self.image, self.rect)
