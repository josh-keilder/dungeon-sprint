import pygame

from globals import (
    BUTTON_FONT_SIZE,
    FONT_PATH,
    MENU_BACKGROUND_COLOR,
    PALETTE_STEEL,
    PALETTE_TORCH,
    SCREEN_WIDTH,
)
from systems import sound
from ui_components.text_button import TextButton

TITLE_FONT_SIZE = 96
TITLE_Y = 50
START_BUTTON_Y = 300
OPTIONS_BUTTON_Y = 380
EXIT_BUTTON_Y = 460

MAIN_MENU_MUSIC = "menu_music"


class MainMenu:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

        self.title_font = pygame.font.Font(FONT_PATH, TITLE_FONT_SIZE)
        self.button_font = pygame.font.Font(FONT_PATH, BUTTON_FONT_SIZE)

        self.title_image = self.title_font.render(
            "DUNGEON SPRINT", False, PALETTE_STEEL
        )
        self.title_pos = ((SCREEN_WIDTH - self.title_image.get_width()) // 2, TITLE_Y)

        self.start_button = TextButton(
            "Start",
            self.button_font,
            (SCREEN_WIDTH // 2, START_BUTTON_Y),
            hover_color=PALETTE_TORCH,
        )
        self.options_button = TextButton(
            "Options",
            self.button_font,
            (SCREEN_WIDTH // 2, OPTIONS_BUTTON_Y),
            hover_color=PALETTE_TORCH,
        )
        self.exit_button = TextButton(
            "Exit",
            self.button_font,
            (SCREEN_WIDTH // 2, EXIT_BUTTON_Y),
            hover_color=PALETTE_TORCH,
        )

    def enter(self):
        sound.play_music(MAIN_MENU_MUSIC)

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
