import pygame

from constants import PALETTE_BLOOD, SCREEN_HEIGHT, SCREEN_WIDTH
from systems.timer import advance_timer, is_running, new_timer, start_timer, time_left

# A red glow around the screen edges when the player is hurt, fading out
VIGNETTE_DURATION = 0.35  # seconds
VIGNETTE_WIDTH = 120  # screen pixels from each edge
VIGNETTE_STEP = 4  # screen pixels per ring of the gradient
VIGNETTE_MAX_ALPHA = 150  # at the very edge, at the start


class HurtVignette:
    def __init__(self):
        self.timer = new_timer()
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Rings from the edge inward, each fainter than the last
        ring_count = VIGNETTE_WIDTH // VIGNETTE_STEP
        for ring in range(ring_count):
            inset = ring * VIGNETTE_STEP
            fade = (1 - ring / ring_count) ** 2
            rect = pygame.Rect(
                inset, inset, SCREEN_WIDTH - 2 * inset, SCREEN_HEIGHT - 2 * inset
            )
            color = (*PALETTE_BLOOD, round(VIGNETTE_MAX_ALPHA * fade))
            pygame.draw.rect(self.overlay, color, rect, VIGNETTE_STEP)

    def start(self):
        start_timer(self.timer, VIGNETTE_DURATION)

    def update(self, dt):
        advance_timer(self.timer, dt)

    def draw(self, screen):
        if not is_running(self.timer):
            return
        self.overlay.set_alpha(round(255 * time_left(self.timer) / VIGNETTE_DURATION))
        screen.blit(self.overlay, (0, 0))
