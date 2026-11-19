import pygame

from engine.io import sound
from engine.ui.text_button import TextButton
from engine.ui.title import make_title
from game.data.constants import BUTTON_FONT_SIZE, FONT_PATH, SCREEN_WIDTH
from game.data.palette import MENU_BACKGROUND_COLOR, PALETTE_STEEL

# Title
TITLE_FONT_SIZE = 96
TITLE_Y = 50  # pixels from the top

# Buttons, by the y of their top edge
START_BUTTON_Y = 300
OPTIONS_BUTTON_Y = 380
EXIT_BUTTON_Y = 460

# Music
MAIN_MENU_MUSIC = "menu_music"


class MainMenu:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

        # Title and button font
        self.button_font = pygame.font.Font(FONT_PATH, BUTTON_FONT_SIZE)
        self.title_image, self.title_pos = make_title(
            "DUNGEON SPRINT", TITLE_FONT_SIZE, PALETTE_STEEL, SCREEN_WIDTH, TITLE_Y
        )

        # Buttons, top to bottom
        self.start_button = TextButton(
            "Start",
            self.button_font,
            (SCREEN_WIDTH // 2, START_BUTTON_Y),
        )
        self.options_button = TextButton(
            "Options",
            self.button_font,
            (SCREEN_WIDTH // 2, OPTIONS_BUTTON_Y),
        )
        self.exit_button = TextButton(
            "Exit",
            self.button_font,
            (SCREEN_WIDTH // 2, EXIT_BUTTON_Y),
        )

    def enter(self):
        sound.play_music(MAIN_MENU_MUSIC)

    def update(self, dt):
        self.start_button.update()
        self.exit_button.update()
        self.options_button.update()

        # Navigation
        if self.start_button.is_clicked():
            self.game_state_manager.set_state("run")

        elif self.options_button.is_clicked():
            self.game_state_manager.set_state("options")

        elif self.exit_button.is_clicked():
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def draw(self, screen):
        screen.fill(MENU_BACKGROUND_COLOR)

        screen.blit(self.title_image, self.title_pos)
        self.start_button.draw(screen)
        self.exit_button.draw(screen)
        self.options_button.draw(screen)
