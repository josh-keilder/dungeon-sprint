import pygame

from globals import (
    FONT_PATH,
    GAME_SCALE,
    PALETTE_BLOOD,
    PALETTE_SHADOW,
    PALETTE_STEEL,
    PALETTE_TORCH,
    PALETTE_VOID,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from systems.assets import load_image
from systems.consumables import HEAL_COOLDOWN
from systems.inventory import count_item
from systems.timer import time_left
from ui_components.panel import make_panel
from ui_components.text_label import TextLabel
from ui_components.time_format import format_run_time

# Shared by every HUD part
PANEL_FRAME_PATH = "Assets/UI/panel_frame.png"
HUD_FONT_SIZE = 24
HUD_MARGIN = 12

# Health panel
HEALTH_PANEL_SIZE = (312, 54)
HEALTH_BAR_OFFSET = (18, 15)
HEALTH_BAR_SIZE = (186, 24)
HEALTH_TEXT_GAP = 9
HEALTH_MAX_SEGMENTS = 5
HEALTH_SEGMENT_STEPS = (5, 10, 20, 25, 50, 100)
HEALTH_SEGMENT_GAP_WIDTH = 3

# Run timer
TIMER_PANEL_SIZE = (162, 54)
TIMER_DIGITS = "0123456789"
TIMER_CHARACTERS = TIMER_DIGITS + ":."

# Quick slots
QUICK_SLOT_SIZE = (72, 72)
QUICK_SLOT_GAP = 12
QUICK_SLOT_ICON_OFFSET = 12
# Inner window of the slot frame; must match the panel art's border
QUICK_SLOT_INNER_OFFSET = 9
QUICK_SLOT_INNER_SIZE = (54, 54)
COOLDOWN_SHADE_ALPHA = 160
EMPTY_ICON_ALPHA = 80


# Helpers
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
    def __init__(self, item_database):
        frame_image = load_image(PANEL_FRAME_PATH)
        self.font = pygame.font.Font(FONT_PATH, HUD_FONT_SIZE)

        # Health panel
        self.health_panel = make_panel(frame_image, HEALTH_PANEL_SIZE)
        self.health_bar_rect = pygame.Rect(
            HUD_MARGIN + HEALTH_BAR_OFFSET[0],
            HUD_MARGIN + HEALTH_BAR_OFFSET[1],
            *HEALTH_BAR_SIZE,
        )

        # Run timer
        self.timer_panel = make_panel(frame_image, TIMER_PANEL_SIZE)
        self.timer_panel_x = (
            (SCREEN_WIDTH - TIMER_PANEL_SIZE[0]) // 2 // GAME_SCALE * GAME_SCALE
        )
        self.timer_glyphs = {
            character: self.font.render(character, False, PALETTE_STEEL)
            for character in TIMER_CHARACTERS
        }
        self.timer_digit_width = max(
            self.timer_glyphs[digit].get_width() for digit in TIMER_DIGITS
        )
        self.timer_text_y = centered_text_y(
            self.timer_glyphs["0"], HUD_MARGIN + TIMER_PANEL_SIZE[1] // 2
        )

        # Quick slots
        self.quick_slot_panel = make_panel(frame_image, QUICK_SLOT_SIZE)
        slot_y = SCREEN_HEIGHT - HUD_MARGIN - QUICK_SLOT_SIZE[1]

        # Potion slot
        self.potion_slot_pos = (HUD_MARGIN, slot_y)
        self.potion_icon = pygame.transform.scale_by(
            item_database["small_health_potion"].image, GAME_SCALE
        )
        self.potion_icon_empty = self.potion_icon.copy()
        self.potion_icon_empty.set_alpha(EMPTY_ICON_ALPHA)
        self.potion_count_label = TextLabel(
            "", color=PALETTE_STEEL, font=self.font, outline_color=PALETTE_VOID
        )
        self.potion_hotkey_label = TextLabel(
            "Q", color=PALETTE_TORCH, font=self.font, outline_color=PALETTE_VOID
        )
        hotkey_label_bounds = self.potion_hotkey_label.text_surface.get_bounding_rect()
        self.potion_hotkey_label.pos = (
            self.potion_slot_pos[0] - hotkey_label_bounds.left,
            self.potion_slot_pos[1] - hotkey_label_bounds.top,
        )

        # Key slot
        self.key_slot_pos = (HUD_MARGIN + QUICK_SLOT_SIZE[0] + QUICK_SLOT_GAP, slot_y)
        self.key_icon = pygame.transform.scale_by(
            item_database["gold_key"].image, GAME_SCALE
        )
        self.key_icon_empty = self.key_icon.copy()
        self.key_icon_empty.set_alpha(EMPTY_ICON_ALPHA)
        self.key_count_label = TextLabel(
            "", color=PALETTE_STEEL, font=self.font, outline_color=PALETTE_VOID
        )

        # Cooldown shade, used by the potion slot
        self.cooldown_shade = pygame.Surface(QUICK_SLOT_INNER_SIZE, pygame.SRCALPHA)
        self.cooldown_shade.fill((0, 0, 0, COOLDOWN_SHADE_ALPHA))

    def draw(self, screen, player, run_time):
        self.draw_health(screen, player.health)
        self.draw_timer(screen, run_time)
        self.draw_quick_slots(screen, player)

    def draw_health(self, screen, health):
        screen.blit(self.health_panel, (HUD_MARGIN, HUD_MARGIN))
        bar_rect = self.health_bar_rect

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
        screen.blit(self.timer_panel, (self.timer_panel_x, HUD_MARGIN))

        timer_string = format_run_time(run_time)

        total_width = sum(
            self.timer_cell_width(character) for character in timer_string
        )

        cursor_x = self.timer_panel_x + (TIMER_PANEL_SIZE[0] - total_width) // 2

        for character in timer_string:
            glyph = self.timer_glyphs[character]
            cell_width = self.timer_cell_width(character)

            glyph_x = cursor_x + (cell_width - glyph.get_width()) // 2

            screen.blit(glyph, (glyph_x, self.timer_text_y))

            cursor_x += cell_width

    def timer_cell_width(self, character):
        if character.isdigit():
            return self.timer_digit_width

        return self.timer_glyphs[character].get_width()

    def draw_quick_slots(self, screen, player):
        potion_cooldown_fraction = time_left(player.heal_cooldown) / HEAL_COOLDOWN

        potion_count = count_item(player.inventory, "small_health_potion")
        potion_icon = self.potion_icon if potion_count > 0 else self.potion_icon_empty
        self.draw_quick_slot(
            screen,
            self.potion_slot_pos,
            potion_icon,
            potion_count,
            self.potion_count_label,
            potion_cooldown_fraction,
        )
        self.potion_hotkey_label.draw(screen)

        key_count = count_item(player.inventory, "gold_key")
        key_icon = self.key_icon if key_count > 0 else self.key_icon_empty
        self.draw_quick_slot(
            screen,
            self.key_slot_pos,
            key_icon,
            key_count,
            self.key_count_label,
        )

    def draw_quick_slot(
        self, screen, slot_pos, icon, count, count_label, cooldown_fraction=0.0
    ):
        icon_pos = (
            slot_pos[0] + QUICK_SLOT_ICON_OFFSET,
            slot_pos[1] + QUICK_SLOT_ICON_OFFSET,
        )
        screen.blit(self.quick_slot_panel, slot_pos)
        screen.blit(icon, icon_pos)

        if cooldown_fraction > 0:
            shade_height = (
                int(self.cooldown_shade.get_height() * cooldown_fraction)
                // GAME_SCALE
                * GAME_SCALE
            )
            inner_pos = (
                slot_pos[0] + QUICK_SLOT_INNER_OFFSET,
                slot_pos[1] + QUICK_SLOT_INNER_OFFSET,
            )
            screen.blit(
                self.cooldown_shade,
                inner_pos,
                pygame.Rect(0, 0, self.cooldown_shade.get_width(), shade_height),
            )

        count_label.update_text(f"x{count}")

        count_bounds = count_label.text_surface.get_bounding_rect()

        slot_right = slot_pos[0] + QUICK_SLOT_SIZE[0]
        slot_bottom = slot_pos[1] + QUICK_SLOT_SIZE[1]
        count_label.pos = (
            slot_right - count_bounds.right - GAME_SCALE,
            slot_bottom - count_bounds.bottom - GAME_SCALE,
        )

        count_label.draw(screen)
