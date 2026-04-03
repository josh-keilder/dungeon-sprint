"""
Main Entry Point: Dungeon Sprint
-------------------------------
This module initializes the Pygame environment and manages the high-level
game loop, including state transitions (menus, levels), event handling,
and global systems like sound and settings.

Classes:
    Game: The primary engine class that coordinates updates and rendering.
"""

import pygame
from globals import *

from states.stateManager import GameStateManager
from states.menus.start import Start
from states.menus.options import Options
from states.map.dungeon_level_one import Dungeon_Level_One
from ui_objects.camera import create_screen
from ui_objects.cursor import Cursor
from ui_objects.text_loader import Text_Loader
from Controllers.sound import SoundController
from settings_manager import SettingsManager


class Game:
    def __init__(self):
        pygame.init()

        # Screen creation is handled by the camera module to support player tracking
        self.screen = create_screen(SCREENWIDTH, SCREENHEIGHT, "Dungeon Sprint")
        self.clock = pygame.time.Clock()
        self.running = True

        # Custom cursor setup
        pygame.mouse.set_visible(False)
        self.cursor_img = pygame.transform.scale_by(
            pygame.image.load("Assets/Cursors/01.png").convert_alpha(), 0.5
        )
        self.cursor = Cursor(self.screen, self.cursor_img)

        self.settings_manager = SettingsManager()
        self.sound_controller = SoundController()

        # FPS UI Setup
        self.fps = None
        self.fps_text = Text_Loader(
            self.fps, self.screen, font_size=15, pos=(1215, 0), color=WHITE
        )

        # State Machine Setup: Handles transitions between menus and gameplay levels
        self.gameStateManager = GameStateManager("start")
        self.start = Start(self.screen, self.gameStateManager, self.cursor)
        self.options = Options(self.screen, self.gameStateManager, self.cursor)
        self.dungeon_level_one = Dungeon_Level_One(
            self.screen, self.gameStateManager, self.cursor
        )

        self.gameStateManager.add_state("dungeon", self.dungeon_level_one)
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

            self.sound_controller.handle_events(event)

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
        self.gameStateManager.get_state().draw()

        if self.settings_manager.get("fps_enabled"):
            self.fps_text.draw()

        self.cursor.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
