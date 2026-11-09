import pygame

from globals import (
    BUTTON_FONT_SIZE,
    FONT_PATH,
    GRAY,
    MENU_BACKGROUND_COLOR,
    SCREEN_WIDTH,
    WHITE,
)
from ui_objects.text_button import TextButton

TITLE_FONT_SIZE = 96
TITLE_Y = 50
START_BUTTON_Y = 300
OPTIONS_BUTTON_Y = 380
EXIT_BUTTON_Y = 460


class Start:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

        self.title_font = pygame.font.Font(FONT_PATH, TITLE_FONT_SIZE)
        self.button_font = pygame.font.Font(FONT_PATH, BUTTON_FONT_SIZE)

        self.title_image = self.title_font.render("DUNGEON SPRINT", False, WHITE)
        self.title_pos = ((SCREEN_WIDTH - self.title_image.get_width()) // 2, TITLE_Y)

        self.start_button = TextButton(
            "Start",
            self.button_font,
            (SCREEN_WIDTH // 2, START_BUTTON_Y),
            outline_color=GRAY,
        )
        self.options_button = TextButton(
            "Options",
            self.button_font,
            (SCREEN_WIDTH // 2, OPTIONS_BUTTON_Y),
            outline_color=GRAY,
        )
        self.exit_button = TextButton(
            "Exit",
            self.button_font,
            (SCREEN_WIDTH // 2, EXIT_BUTTON_Y),
            outline_color=GRAY,
        )

    def draw(self, screen):
        screen.fill(MENU_BACKGROUND_COLOR)

        screen.blit(self.title_image, self.title_pos)
        self.start_button.draw(screen)
        self.exit_button.draw(screen)
        self.options_button.draw(screen)

    def update(self, dt):
        self.start_button.update()
        self.exit_button.update()
        self.options_button.update()

        # Navigation Logic
        if self.start_button.is_clicked():
            self.game_state_manager.set_state("level")

        elif self.options_button.is_clicked():
            self.game_state_manager.set_state("options")

        elif self.exit_button.is_clicked():
            pygame.event.post(pygame.event.Event(pygame.QUIT))
