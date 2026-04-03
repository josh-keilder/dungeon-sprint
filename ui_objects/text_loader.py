"""
UI Component: Text Loader
-------------------------
A utility class for rendering and displaying text in Pygame. It handles
font initialization, surface creation (rendering), and drawing to the screen.

Classes:
    Text_Loader: Manages a single text surface with update capabilities.
"""

import pygame
from globals import *


class Text_Loader:
    def __init__(
        self,
        text,
        screen,
        font_name="Comic Sans MS",
        font_size=30,
        color=BLACK,
        pos=(0, 0),
    ):
        """
        Initializes the font and creates the initial text surface.

        Args:
            text (str): The initial string to display.
            screen (pygame.Surface): The target surface for drawing.
            font_name (str): System font name.
            font_size (int): Size of the font in pixels.
            color (tuple): RGB color of the text.
            pos (tuple): Default (x, y) coordinates for placement.
        """
        pygame.font.init()
        self.font = pygame.font.SysFont(font_name, font_size)
        self.screen = screen
        self.color = color
        self.pos = pos
        self.text = text

        # Initial render: False indicates no anti-aliasing for a crisper pixel look
        self.text_surface = self.font.render(str(self.text), False, self.color)

    def draw(self, specific_pos=None):
        """
        Blits the text surface onto the screen.

        Args:
            specific_pos (tuple, optional): Overrides the default position if provided.
        """
        pos_to_use = specific_pos if specific_pos else self.pos
        self.screen.blit(self.text_surface, pos_to_use)

    def update_text(self, new_text):
        """Re-renders the text surface with new content."""
        self.text = new_text
        self.text_surface = self.font.render(str(self.text), False, self.color)
