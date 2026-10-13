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
        self.cursor_img = pygame.transform.scale_by(
            pygame.image.load("Assets/Cursors/01.png").convert_alpha(), 0.5
        )
        self.cursor = Cursor(self.cursor_img)

        # Load settings and set initial sound volumes
        music_volume = settings.get_setting("music_volume")
        sfx_volume = settings.get_setting("sfx_volume")
        sound.load_sfx()
        sound.load_music()
        sound.set_sfx_volume(sfx_volume)
        sound.set_music_volume(music_volume)

        # FPS UI Setup
        self.fps = None
        self.fps_text = Text_Loader(self.fps, font_size=15, pos=(1215, 0), color=WHITE)

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

        pygame.display.update()

        # Performance monitoring: Update FPS display approximately every 0.5 seconds
        if pygame.time.get_ticks() % 500 < 20:
            self.fps = self.clock.get_fps()
            self.fps_text.update_text(f"FPS: {int(self.fps)}")

    def draw(self):
        """Renders the current state and global UI elements to the screen."""
        screen = pygame.display.get_surface()
        self.gameStateManager.get_state().draw(screen)

        if settings.get_setting("fps_enabled"):
            self.fps_text.draw(screen)

        self.cursor.draw(screen)


if __name__ == "__main__":
    game = Game()
    game.run()
