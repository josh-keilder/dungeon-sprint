import pygame

from engine.graphics.display import get_mouse_pos
from engine.ui.theme import get_theme, play_theme_sound

# Knob shape, in pixels
KNOB_WIDTH = 20
KNOB_OVERHANG = 5  # how far the knob sticks out above and below the track

# Rounded corners, in pixels
TRACK_CORNER_RADIUS = 5
KNOB_CORNER_RADIUS = 3


class Slider:
    def __init__(
        self,
        pos,
        size,
        initial_value,
        min_value,
        max_value,
        track_color,
        knob_color,
    ):
        # Placement: pos is the track's center
        self.pos = pos
        self.size = size

        # The range, and the value the knob is at
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value

        # Boundary calculations for clamping movement
        self.left_x = self.pos[0] - (size[0] // 2)
        self.right_x = self.pos[0] + (size[0] // 2)
        self.top_y = self.pos[1] - (size[1] // 2)

        # Track setup
        self.track_rect = pygame.Rect(
            self.left_x, self.top_y, self.size[0], self.size[1]
        )
        self.track_color = track_color

        # Knob setup
        self.knob_rect = pygame.Rect(
            0, self.top_y - KNOB_OVERHANG, KNOB_WIDTH, self.size[1] + 2 * KNOB_OVERHANG
        )
        self.set_knob_position_from_value(initial_value)
        self.knob_color = knob_color

        # Mouse state, refreshed by update
        self.dragging = False
        self.hovered = False

    def update(self):
        mouse_pos = get_mouse_pos()
        mouse_held = pygame.mouse.get_pressed()[0]

        # Hover detection
        if self.knob_rect.collidepoint(mouse_pos) or self.track_rect.collidepoint(
            mouse_pos
        ):
            if not self.hovered:
                play_theme_sound("hover_sound")
            self.hovered = True
        else:
            self.hovered = False

        # Start dragging on a press over the slider; stop on release
        if self.hovered and mouse_held:
            self.dragging = True

        if not mouse_held:
            self.dragging = False

        if self.dragging:
            # Constrain knob movement to the track length
            knob_x = max(self.left_x, min(mouse_pos[0], self.right_x))
            self.knob_rect.centerx = knob_x
            self.value = self.get_value_from_knob_position()

    def draw(self, screen):
        # Main background track
        pygame.draw.rect(
            screen,
            get_theme("slider_empty_color"),
            self.track_rect,
            border_radius=TRACK_CORNER_RADIUS,
        )

        # "Progress" fill: shows the distance between the start and the knob
        filled_rect = pygame.Rect(
            self.left_x,
            self.top_y,
            self.knob_rect.centerx - self.left_x,
            self.size[1],
        )
        pygame.draw.rect(
            screen, self.track_color, filled_rect, border_radius=TRACK_CORNER_RADIUS
        )

        # Knob rendering with visual feedback for interaction
        color = (
            get_theme("hover_color")
            if self.hovered or self.dragging
            else self.knob_color
        )
        pygame.draw.rect(
            screen, color, self.knob_rect, border_radius=KNOB_CORNER_RADIUS
        )

    def get_current_value(self):
        return int(self.value)

    def set_knob_position_from_value(self, value):
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        self.knob_rect.centerx = self.left_x + (ratio * self.size[0])

    def get_value_from_knob_position(self):
        ratio = (self.knob_rect.centerx - self.left_x) / self.size[0]
        return self.min_value + (ratio * (self.max_value - self.min_value))
