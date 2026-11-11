import pygame

from globals import (
    FONT_PATH,
    GAME_SCALE,
    PALETTE_BLOOD,
    PALETTE_SHADOW,
    PALETTE_STEEL,
    PALETTE_VOID,
    SCREEN_WIDTH,
)
from systems.assets import load_image
from ui_components.panel import make_panel
from ui_components.time_format import format_run_time

PANEL_FRAME_PATH = "Assets/UI/panel_frame.png"

HUD_FONT_SIZE = 24
HUD_MARGIN = 12

# Health Constants
HEALTH_PANEL_SIZE = (312, 54)
HEALTH_BAR_OFFSET = (18, 15)
HEALTH_BAR_SIZE = (186, 24)
HEALTH_TEXT_GAP = 9
HEALTH_MAX_SEGMENTS = 5
HEALTH_SEGMENT_STEPS = (5, 10, 20, 25, 50, 100)
HEALTH_SEGMENT_GAP_WIDTH = 3

# Timer Constants
TIMER_PANEL_SIZE = (162, 54)


def segment_hp_for(max_health):
    for step in HEALTH_SEGMENT_STEPS:
        if max_health / step <= HEALTH_MAX_SEGMENTS:
            return step

    return HEALTH_SEGMENT_STEPS[-1]


def centered_text_y(text_surface, center_y):
    text_bounds = text_surface.get_bounding_rect()
    text_y = center_y - text_bounds.centery
    text_y = text_y // GAME_SCALE * GAME_SCALE

    return text_y


class HUD:
    def __init__(self):
        frame_image = load_image(PANEL_FRAME_PATH)
        self.font = pygame.font.Font(FONT_PATH, HUD_FONT_SIZE)

        self.health_panel = make_panel(frame_image, HEALTH_PANEL_SIZE)

        self.timer_panel = make_panel(frame_image, TIMER_PANEL_SIZE)
        self.timer_glyphs = {
            character: self.font.render(character, False, PALETTE_STEEL)
            for character in "0123456789:."
        }
        self.timer_digit_width = max(
            self.timer_glyphs[digit].get_width() for digit in "0123456789"
        )

    def draw_health(self, screen, health):
        screen.blit(self.health_panel, (HUD_MARGIN, HUD_MARGIN))
        bar_rect = pygame.Rect(
            HUD_MARGIN + HEALTH_BAR_OFFSET[0],
            HUD_MARGIN + HEALTH_BAR_OFFSET[1],
            *HEALTH_BAR_SIZE,
        )

        pygame.draw.rect(screen, PALETTE_SHADOW, bar_rect)

        health_ratio = health["current"] / health["max_health"]
        fill_width = int(bar_rect.width * health_ratio) // GAME_SCALE * GAME_SCALE
        pygame.draw.rect(
            screen, PALETTE_BLOOD, (bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
        )

        segment_hp = segment_hp_for(health["max_health"])
        for gap_hp in range(segment_hp, health["max_health"], segment_hp):
            gap_offset = (
                int(bar_rect.width * gap_hp / health["max_health"])
                // GAME_SCALE
                * GAME_SCALE
            )

            pygame.draw.rect(
                screen,
                PALETTE_VOID,
                (
                    bar_rect.x + gap_offset,
                    bar_rect.y,
                    HEALTH_SEGMENT_GAP_WIDTH,
                    bar_rect.height,
                ),
            )

        health_text = self.font.render(
            f"{health['current']}/{health['max_health']}", False, PALETTE_STEEL
        )
        text_y = centered_text_y(health_text, bar_rect.centery)
        screen.blit(health_text, (bar_rect.right + HEALTH_TEXT_GAP, text_y))

    def draw_timer(self, screen, run_time):
        panel_x = (SCREEN_WIDTH - TIMER_PANEL_SIZE[0]) // 2 // GAME_SCALE * GAME_SCALE

        screen.blit(self.timer_panel, (panel_x, HUD_MARGIN))

        timer_string = format_run_time(run_time)

        total_width = sum(
            self.timer_cell_width(character) for character in timer_string
        )

        cursor_x = panel_x + (TIMER_PANEL_SIZE[0] - total_width) // 2

        text_y = centered_text_y(
            self.timer_glyphs["0"], HUD_MARGIN + TIMER_PANEL_SIZE[1] // 2
        )

        for character in timer_string:
            glyph = self.timer_glyphs[character]
            cell_width = self.timer_cell_width(character)

            glyph_x = cursor_x + (cell_width - glyph.get_width()) // 2

            screen.blit(glyph, (glyph_x, text_y))

            cursor_x += cell_width

    def timer_cell_width(self, character):
        if character.isdigit():
            return self.timer_digit_width

        return self.timer_glyphs[character].get_width()

    def draw(self, screen, player, run_time):
        self.draw_health(screen, player.health)
        self.draw_timer(screen, run_time)
