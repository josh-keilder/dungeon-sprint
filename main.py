import pygame

from constants import FRAME_RATE, GREEN, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from engine.core.assets import load_image
from engine.core.state_manager import GameStateManager
from engine.graphics.display import create_window
from states.menus.main_menu import MainMenu
from states.menus.options import OptionsMenu
from states.menus.run_end import RunEndScreen
from states.run import Run
from systems import settings, sound
from systems.renderer import Renderer
from ui_components.cursor import Cursor
from ui_components.fps_counter import FpsCounter

# Cursor art
CURSOR_IMAGE_PATH = "Assets/Cursors/01.png"

# Music for the death screen (the finish screen keeps the level music)
GAME_OVER_MUSIC = "game_over"


class Game:
    def __init__(self):
        pygame.init()

        settings.load_settings()

        create_window(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            settings.get_setting("full_screen_enabled"),
            WINDOW_TITLE,
        )

        # Every frame is drawn on ui_surface (transparent), then the renderer puts the
        # world (if a run submitted one) and this surface into the window
        self.renderer = Renderer()
        self.ui_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

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

        # FPS counter, shown when the setting is on
        self.fps_counter = FpsCounter()

        # Screens, and the manager that switches between them
        self.game_state_manager = GameStateManager("main_menu")
        self.main_menu = MainMenu(self.game_state_manager)
        self.options_menu = OptionsMenu(self.game_state_manager)
        self.run_state = Run(self.game_state_manager)
        self.game_over_screen = RunEndScreen(
            self.game_state_manager, "You Died!", RED, GAME_OVER_MUSIC
        )
        self.run_complete_screen = RunEndScreen(
            self.game_state_manager, "You Escaped!", GREEN, None
        )

        self.game_state_manager.add_state("run", self.run_state)
        self.game_state_manager.add_state("options", self.options_menu)
        self.game_state_manager.add_state("main_menu", self.main_menu)
        self.game_state_manager.add_state("game_over", self.game_over_screen)
        self.game_state_manager.add_state("run_complete", self.run_complete_screen)

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

        self.fps_counter.update(self.dt, self.clock.get_fps())

    def draw(self):
        self.ui_surface.fill((0, 0, 0, 0))
        self.game_state_manager.get_state().draw(self.ui_surface)

        if settings.get_setting("fps_enabled"):
            self.fps_counter.draw(self.ui_surface)

        self.cursor.draw(self.ui_surface)

        self.renderer.present(self.ui_surface)
        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
