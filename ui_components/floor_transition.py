import pygame

from constants import PALETTE_VOID, SCREEN_HEIGHT, SCREEN_WIDTH
from engine.core.timer import (
    advance_timer,
    is_running,
    new_timer,
    start_timer,
    time_left,
)
from engine.ui.text_label import TextLabel
from engine.ui.text_layout import centered_text_x, centered_text_y

# Phase lengths
FADE_DURATION = 0.4  # seconds, each way
FLOOR_CARD_DURATION = 1.0  # seconds

# Loading a floor takes real time; one transition frame never counts as more than this
MAX_TRANSITION_DT = 1 / 30  # seconds

# The "Floor N" card
FLOOR_CARD_FONT_SIZE = 48


class FloorTransition:
    def __init__(self):
        # None while playing, else "fade_out", "card" or "fade_in"
        self.phase = None
        self.timer = new_timer()

        # A screen-sized black overlay, faded in and out over everything
        self.fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_overlay.fill(PALETTE_VOID)
        self.floor_label = TextLabel("", font_size=FLOOR_CARD_FONT_SIZE)

    def start(self):
        self.phase = "fade_out"
        start_timer(self.timer, FADE_DURATION)

    def is_active(self):
        return self.phase is not None

    def update(self, dt):
        advance_timer(self.timer, min(dt, MAX_TRANSITION_DT))
        if is_running(self.timer):
            return False

        if self.phase == "fade_out":
            self.phase = "card"
            start_timer(self.timer, FLOOR_CARD_DURATION)
            return True

        if self.phase == "card":
            self.phase = "fade_in"
            start_timer(self.timer, FADE_DURATION)
        else:
            self.phase = None
        return False

    def draw(self, screen):
        if self.phase is None:
            return

        self.fade_overlay.set_alpha(self.overlay_alpha())
        screen.blit(self.fade_overlay, (0, 0))

        if self.phase == "card":
            self.floor_label.draw(screen)

    def set_floor_number(self, floor_number):
        self.floor_label.update_text(f"Floor {floor_number}")
        text_surface = self.floor_label.text_surface
        self.floor_label.pos = (
            centered_text_x(text_surface, SCREEN_WIDTH // 2),
            centered_text_y(text_surface, SCREEN_HEIGHT // 2),
        )

    def overlay_alpha(self):
        fade_left = time_left(self.timer) / FADE_DURATION

        if self.phase == "fade_out":
            return round(255 * (1 - fade_left))
        if self.phase == "fade_in":
            return round(255 * fade_left)
        return 255
