import pygame

from globals import (
    DUNGEON_LEVEL_ONE,
    FONT_PATH,
    GREEN,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)
from states.map.level import Level
from ui_objects.button import Button

TITLE_FONT_SIZE = 64
BUTTON_FONT_SIZE = 32
TITLE_Y = 200
RESTART_BUTTON_Y = 380
MAIN_MENU_BUTTON_Y = 460
OVERLAY_ALPHA = 160


class GameOver:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

        self.title_font = pygame.font.Font(FONT_PATH, TITLE_FONT_SIZE)
        self.button_font = pygame.font.Font(FONT_PATH, BUTTON_FONT_SIZE)

        self.title_image = self.title_font.render("You Died!", False, RED)
        self.title_pos = ((SCREEN_WIDTH - self.title_image.get_width()) // 2, TITLE_Y)

        restart_image = self.button_font.render("Restart", False, WHITE)
        self.restart_button = Button(
            restart_image,
            pos=((SCREEN_WIDTH - restart_image.get_width()) // 2, RESTART_BUTTON_Y),
            outline_color=GREEN,
        )

        main_menu_image = self.button_font.render("Main Menu", False, WHITE)
        self.main_menu_button = Button(
            main_menu_image,
            pos=((SCREEN_WIDTH - main_menu_image.get_width()) // 2, MAIN_MENU_BUTTON_Y),
            outline_color=GREEN,
        )

        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, OVERLAY_ALPHA))

    def start_new_run(self):
        new_level = Level(self.game_state_manager, DUNGEON_LEVEL_ONE)

        self.game_state_manager.add_state("level", new_level)

    def update(self, dt):
        self.restart_button.update()
        self.main_menu_button.update()

        if self.main_menu_button.is_clicked():
            self.start_new_run()
            self.game_state_manager.set_state("start")

        if self.restart_button.is_clicked():
            self.start_new_run()
            self.game_state_manager.set_state("level")

    def draw(self, screen):
        self.game_state_manager.states["level"].draw(screen)
        screen.blit(self.overlay, (0, 0))
        screen.blit(self.title_image, self.title_pos)
        self.restart_button.draw(screen)
        self.main_menu_button.draw(screen)
