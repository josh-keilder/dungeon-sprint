import pygame

from globals import (
    BUTTON_FONT_SIZE,
    FONT_PATH,
    GRAY,
    OVERLAY_ALPHA,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)
from states.new_run import start_new_run
from systems import sound
from ui_objects.text_button import TextButton
from ui_objects.time_format import format_run_time

TITLE_FONT_SIZE = 64
TITLE_Y = 200
RESTART_BUTTON_Y = 380
MAIN_MENU_BUTTON_Y = 460

RUN_TIME_Y = 290


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
            outline_color=GRAY,
        )

        self.main_menu_button = TextButton(
            "Main Menu",
            self.button_font,
            (SCREEN_WIDTH // 2, MAIN_MENU_BUTTON_Y),
            outline_color=GRAY,
        )

        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, OVERLAY_ALPHA))

        self.render_run_time(0.0)

    def enter(self):
        run_time = self.game_state_manager.states["level"].run_time
        self.render_run_time(run_time)

        if self.music is not None:
            sound.stop_music()
            sound.play_music(self.music, loops=0)

    def render_run_time(self, run_time):
        self.run_time_image = self.button_font.render(
            f"Time: {format_run_time(run_time)}", False, WHITE
        )
        self.run_time_pos = (
            (SCREEN_WIDTH - self.run_time_image.get_width()) // 2,
            RUN_TIME_Y,
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
        screen.blit(self.run_time_image, self.run_time_pos)
        self.restart_button.draw(screen)
        self.main_menu_button.draw(screen)
