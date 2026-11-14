import pygame

from globals import (
    BUTTON_FONT_SIZE,
    FONT_PATH,
    OVERLAY_ALPHA,
    PALETTE_BLOOD,
    PALETTE_SHADOW,
    PALETTE_STEEL,
    PALETTE_TORCH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from states.new_run import start_new_run
from systems import sound
from ui_components.text_button import TextButton
from ui_components.time_format import format_run_time, to_centiseconds

TITLE_FONT_SIZE = 64
TITLE_Y = 120

SPLITS_TOP_Y = 230
SPLIT_ROW_HEIGHT = 42
SPLIT_LABEL_X = SCREEN_WIDTH // 2 - 180
SPLIT_TIME_RIGHT = SCREEN_WIDTH // 2 + 180
SPLIT_TOTAL_GAP = 18
SPLIT_DIVIDER_HEIGHT = 3

RESTART_BUTTON_Y = 540
MAIN_MENU_BUTTON_Y = 610


def floor_times(splits, run_time):
    times = []
    previous_centiseconds = 0

    for split in splits:
        split_centiseconds = to_centiseconds(split)
        times.append((split_centiseconds - previous_centiseconds) / 100)
        previous_centiseconds = split_centiseconds

    # Died partway through a floor: add the time spent on it so far
    run_centiseconds = to_centiseconds(run_time)
    if run_centiseconds > previous_centiseconds:
        times.append((run_centiseconds - previous_centiseconds) / 100)

    return times


class RunEndScreen:
    def __init__(self, game_state_manager, title, title_color, music):
        self.game_state_manager = game_state_manager

        self.title_font = pygame.font.Font(FONT_PATH, TITLE_FONT_SIZE)
        self.button_font = pygame.font.Font(FONT_PATH, BUTTON_FONT_SIZE)

        self.title_image = self.title_font.render(title, False, title_color)
        self.title_pos = ((SCREEN_WIDTH - self.title_image.get_width()) // 2, TITLE_Y)

        self.music = music

        self.restart_button = TextButton(
            "Restart",
            self.button_font,
            (SCREEN_WIDTH // 2, RESTART_BUTTON_Y),
            hover_color=PALETTE_TORCH,
        )

        self.main_menu_button = TextButton(
            "Main Menu",
            self.button_font,
            (SCREEN_WIDTH // 2, MAIN_MENU_BUTTON_Y),
            hover_color=PALETTE_TORCH,
        )

        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, OVERLAY_ALPHA))

        self.split_rows = []
        self.divider_rect = pygame.Rect(0, 0, 0, 0)

    def enter(self):
        level = self.game_state_manager.states["level"]
        self.render_splits(level.splits, level.run_time, level.dying)

        if self.music is not None:
            sound.stop_music()
            sound.play_music(self.music, loops=0)

    def render_splits(self, splits, run_time, died):
        self.split_rows = []
        times = floor_times(splits, run_time)

        for floor_index, seconds in enumerate(times):
            died_here = died and floor_index == len(times) - 1
            color = PALETTE_BLOOD if died_here else PALETTE_STEEL
            row_y = SPLITS_TOP_Y + floor_index * SPLIT_ROW_HEIGHT
            self.add_split_row(f"Floor {floor_index + 1}", seconds, row_y, color)

        divider_y = SPLITS_TOP_Y + len(times) * SPLIT_ROW_HEIGHT
        self.divider_rect = pygame.Rect(
            SPLIT_LABEL_X,
            divider_y,
            SPLIT_TIME_RIGHT - SPLIT_LABEL_X,
            SPLIT_DIVIDER_HEIGHT,
        )

        total_y = divider_y + SPLIT_TOTAL_GAP
        self.add_split_row("Total", run_time, total_y, PALETTE_STEEL)

    def add_split_row(self, label, seconds, row_y, color):
        label_image = self.button_font.render(label, False, color)
        time_image = self.button_font.render(format_run_time(seconds), False, color)

        self.split_rows.append((label_image, (SPLIT_LABEL_X, row_y)))
        self.split_rows.append(
            (time_image, (SPLIT_TIME_RIGHT - time_image.get_width(), row_y))
        )

    def update(self, dt):
        self.restart_button.update()
        self.main_menu_button.update()

        if self.main_menu_button.is_clicked():
            start_new_run(self.game_state_manager)
            self.game_state_manager.set_state("main_menu")

        if self.restart_button.is_clicked():
            start_new_run(self.game_state_manager)
            self.game_state_manager.set_state("level")

    def draw(self, screen):
        self.game_state_manager.states["level"].draw(screen)
        screen.blit(self.overlay, (0, 0))
        screen.blit(self.title_image, self.title_pos)
        for image, pos in self.split_rows:
            screen.blit(image, pos)
        pygame.draw.rect(screen, PALETTE_SHADOW, self.divider_rect)
        self.restart_button.draw(screen)
        self.main_menu_button.draw(screen)
