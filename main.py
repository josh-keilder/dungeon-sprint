import pygame

from globals import (
    DUNGEON_LEVEL_ONE,
    FRAME_RATE,
    GREEN,
    PALETTE_STEEL,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from states.map.level import Level
from states.menus.main_menu import MainMenu
from states.menus.options import Options
from states.menus.run_end import RunEndScreen
from states.state_manager import GameStateManager
from systems import settings, sound
from systems.assets import load_image
from systems.display import create_window
from ui_components.cursor import Cursor
from ui_components.text_label import TextLabel

CURSOR_IMAGE_PATH = "Assets/Cursors/01.png"

FPS_REFRESH_INTERVAL = 0.5

GAME_OVER_MUSIC = "game_over"


class Game:
    def __init__(self):
        pygame.init()

        settings.load_settings()

        create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, settings.get_setting("full_screen_enabled")
        )
        self.clock = pygame.time.Clock()
        self.running = True

        # Custom cursor setup
        pygame.mouse.set_visible(False)
        cursor_image = pygame.transform.scale_by(load_image(CURSOR_IMAGE_PATH), 0.5)
        self.cursor = Cursor(cursor_image)

        # Sound: load files and apply saved volumes
        music_volume = settings.get_setting("music_volume")
        sfx_volume = settings.get_setting("sfx_volume")
        sound.load_sfx()
        sound.load_music()
        sound.set_sfx_volume(sfx_volume)
        sound.set_music_volume(music_volume)

        # FPS counter
        self.fps_timer = 0.0
        self.fps_text = TextLabel("", font_size=15, pos=(1215, 0), color=PALETTE_STEEL)

        # Screens, and the manager that switches between them
        self.game_state_manager = GameStateManager("main_menu")
        self.main_menu = MainMenu(self.game_state_manager)
        self.options_menu = Options(self.game_state_manager)
        self.level = Level(self.game_state_manager, DUNGEON_LEVEL_ONE)
        self.game_over_screen = RunEndScreen(
            self.game_state_manager, "You Died!", RED, GAME_OVER_MUSIC
        )
        self.level_complete_screen = RunEndScreen(
            self.game_state_manager, "You Escaped!", GREEN, None
        )

        self.game_state_manager.add_state("level", self.level)
        self.game_state_manager.add_state("options", self.options_menu)
        self.game_state_manager.add_state("main_menu", self.main_menu)
        self.game_state_manager.add_state("game_over", self.game_over_screen)
        self.game_state_manager.add_state("level_complete", self.level_complete_screen)

        self.game_state_manager.get_state().enter()

    def run(self):
        while self.running:
            self.update()
            self.draw()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Seconds since the last frame
        self.dt = self.clock.tick(FRAME_RATE) / 1000.0

        self.game_state_manager.get_state().update(self.dt)
        self.cursor.update()

        self.fps_timer += self.dt
        if self.fps_timer >= FPS_REFRESH_INTERVAL:
            self.fps_timer -= FPS_REFRESH_INTERVAL
            self.fps_text.update_text(f"FPS: {int(self.clock.get_fps())}")

    def draw(self):
        screen = pygame.display.get_surface()
        self.game_state_manager.get_state().draw(screen)

        if settings.get_setting("fps_enabled"):
            self.fps_text.draw(screen)

        self.cursor.draw(screen)

        pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
