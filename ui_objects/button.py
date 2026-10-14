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

from globals import WHITE
from systems import sound
from ui_objects.create_outline import draw_outline, make_outline


class Button:
    def __init__(self, image, pos=(0, 0)):
        """
        Initializes the button with an image and position.

        Args:
            screen (pygame.Surface): The surface to draw the button on.
            image (pygame.Surface): The sprite used for the button face.
            pos (tuple): The (x, y) coordinates for the top-left corner.
        """
        self.image = image
        self.outline = make_outline(self.image, WHITE)
        self.rect = self.image.get_frect()
        self.rect.topleft = pos
        self.hovered = False
        self.clicked_this_frame = False

    def draw(self, screen):
        """Renders the button and its hover outline to the screen."""
        screen.blit(self.image, (self.rect.x, self.rect.y))

        if self.hovered:
            draw_outline(screen, self.outline, (self.rect.x, self.rect.y))

    def update(self):
        """Updates the hover state and triggers hover sound effects."""
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if not self.hovered:
                sound.play_sfx("Button_Hover")
                self.hovered = True
        else:
            self.hovered = False

        self.clicked_this_frame = self.hovered and pygame.mouse.get_just_pressed()[0]

        if self.clicked_this_frame:
            sound.play_sfx("Button_Click")

    def is_clicked(self) -> bool:
        return self.clicked_this_frame

    def set_image(self, image):
        self.image = image
        self.outline = make_outline(image, WHITE)
        self.rect = image.get_frect(topleft=self.rect.topleft)
