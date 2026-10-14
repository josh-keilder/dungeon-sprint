import pygame
from globals import *

from states.stateManager import GameStateManager
from states.menus.start import Start
from states.menus.options import Options
from states.map.level import Level
from ui_objects.cursor import Cursor
from ui_objects.text_loader import Text_Loader
from systems import sound, settings
from systems.display import create_window
from systems.assets import load_image

TITLE_MUSIC = "JuiceWrldChasingTheDragon"

CURSOR_IMAGE_PATH = "Assets/Cursors/01.png"

FPS_REFRESH_INTERVAL = 0.5


class Game:
    def __init__(self):
        pygame.init()

        settings.load_settings()

        create_window(
            SCREENWIDTH, SCREENHEIGHT, settings.get_setting("full_screen_enabled")
        )
        self.clock = pygame.time.Clock()
        self.running = True

        # Custom cursor setup
        pygame.mouse.set_visible(False)
        cursor_img = pygame.transform.scale_by(load_image(CURSOR_IMAGE_PATH), 0.5)
        self.cursor = Cursor(cursor_img)

        # Load settings and set initial sound volumes
        music_volume = settings.get_setting("music_volume")
        sfx_volume = settings.get_setting("sfx_volume")
        sound.load_sfx()
        sound.load_music()
        sound.set_sfx_volume(sfx_volume)
        sound.set_music_volume(music_volume)
        sound.play_music(TITLE_MUSIC)

        # FPS UI Setup
        self.fps_timer = 0.0
        self.fps_text = Text_Loader("", font_size=15, pos=(1215, 0), color=WHITE)

        # State Machine Setup: Handles transitions between menus and gameplay levels
        self.gameStateManager = GameStateManager("start")
        self.start = Start(self.gameStateManager)
        self.options = Options(self.gameStateManager)
        self.level = Level(self.gameStateManager, DUNGEON_LEVEL_ONE)

        self.gameStateManager.add_state("level", self.level)
        self.gameStateManager.add_state("options", self.options)
        self.gameStateManager.add_state("start", self.start)

    def run(self):
        """Main game loop."""
        while self.running:
            self.update()
            self.draw()

    def update(self):
        """Processes input events, updates delta time, and updates the active state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Calculate Delta Time (seconds)
        self.dt = self.clock.tick(FRAMERATE) / 1000.0

        # Update current active state (Menu/Level)
        self.gameStateManager.get_state().update(self.dt)
        self.cursor.update()

        self.fps_timer += self.dt
        if self.fps_timer >= FPS_REFRESH_INTERVAL:
            self.fps_timer -= FPS_REFRESH_INTERVAL
            self.fps_text.update_text(f"FPS: {int(self.clock.get_fps())}")

    def draw(self):
        """Renders the current state and global UI elements to the screen."""
        screen = pygame.display.get_surface()
        self.gameStateManager.get_state().draw(screen)

        if settings.get_setting("fps_enabled"):
            self.fps_text.draw(screen)

        self.cursor.draw(screen)

        pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
