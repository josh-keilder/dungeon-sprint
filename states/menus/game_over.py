import pygame

from globals import (
    BUTTON_FONT_SIZE,
    FONT_PATH,
    GRAY,
    OVERLAY_ALPHA,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from states.new_run import start_new_run
from ui_objects.text_button import TextButton

TITLE_FONT_SIZE = 64
TITLE_Y = 200
RESTART_BUTTON_Y = 380
MAIN_MENU_BUTTON_Y = 460


class GameOver:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

        self.title_font = pygame.font.Font(FONT_PATH, TITLE_FONT_SIZE)
        self.button_font = pygame.font.Font(FONT_PATH, BUTTON_FONT_SIZE)

        self.title_image = self.title_font.render("You Died!", False, RED)
        self.title_pos = ((SCREEN_WIDTH - self.title_image.get_width()) // 2, TITLE_Y)

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
        self.restart_button.draw(screen)
        self.main_menu_button.draw(screen)
