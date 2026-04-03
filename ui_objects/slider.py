"""
UI Component: Slider
--------------------
Provides an interactive horizontal slider for settings menus (e.g., volume
control). Handles mouse collision, dragging logic, and value mapping
between pixel coordinates and numerical ranges.

Classes:
    Slider: A customizable UI element that returns a value within a set range.
"""

import pygame
from globals import *
from Controllers.sound import SoundController


class Slider:
    def __init__(
        self,
        screen,
        pos,
        size,
        initial_value,
        min_val,
        max_val,
        track_color,
        knob_color,
    ):
        """
        Initializes the slider and calculates its interactive boundaries.

        Args:
            screen (pygame.Surface): Target surface for rendering.
            pos (tuple): (x, y) center position of the slider.
            size (tuple): (width, height) of the slider track.
            initial_value (float): Starting value.
            min_val (float): Minimum possible value.
            max_val (float): Maximum possible value.
        """
        self.screen = screen
        self.pos = pos
        self.size = size

        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_value

        # Boundary calculations for clamping movement
        self.left_x = self.pos[0] - (size[0] // 2)
        self.right_x = self.pos[0] + (size[0] // 2)
        self.top_y = self.pos[1] - (size[1] // 2)

        # Track Setup
        self.container_rect = pygame.Rect(
            self.left_x, self.top_y, self.size[0], self.size[1]
        )
        self.track_color = track_color

        # Knob Setup
        knob_width = 20
        self.button_rect = pygame.Rect(0, self.top_y - 5, knob_width, self.size[1] + 10)
        self.set_knob_pos_from_value(initial_value)
        self.knob_color = knob_color

        self.dragging = False
        self.hovered = False
        self.sound_controller = SoundController()

    def set_knob_pos_from_value(self, val):
        """Maps a numerical value (e.g., 0-100) to a pixel position on the track."""
        ratio = (val - self.min_val) / (self.max_val - self.min_val)
        self.button_rect.centerx = self.left_x + (ratio * self.size[0])

    def get_value_from_pos(self):
        """Maps the current knob pixel position back to a numerical value."""
        ratio = (self.button_rect.centerx - self.left_x) / self.size[0]
        return self.min_val + (ratio * (self.max_val - self.min_val))

    def update(self):
        """Processes mouse interaction, hover states, and drag-and-drop logic."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        # Hover Detection
        if self.button_rect.collidepoint(mouse_pos) or self.container_rect.collidepoint(
            mouse_pos
        ):
            if not self.hovered:
                self.sound_controller.play_sfx("Button_Hover")
            self.hovered = True
        else:
            self.hovered = False

        # State Management
        if self.hovered and mouse_click:
            self.dragging = True

        if not mouse_click:
            self.dragging = False

        if self.dragging:
            # Constrain knob movement to the track length
            new_x = max(self.left_x, min(mouse_pos[0], self.right_x))
            self.button_rect.centerx = new_x
            self.value = self.get_value_from_pos()

    def draw(self):
        """Renders the track background, filled progress, and the interactive knob."""
        # Main background track
        pygame.draw.rect(self.screen, GRAY, self.container_rect, border_radius=5)

        # "Progress" fill: shows the distance between the start and the knob
        filled_rect = pygame.Rect(
            self.left_x,
            self.top_y,
            self.button_rect.centerx - self.left_x,
            self.size[1],
        )
        pygame.draw.rect(self.screen, self.track_color, filled_rect, border_radius=5)

        # Knob rendering with visual feedback for interaction
        color = WHITE if self.hovered or self.dragging else LIGHT_GRAY
        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=3)

    def get_current_value(self):
        """Returns the current slider value as an integer."""
        return int(self.value)
