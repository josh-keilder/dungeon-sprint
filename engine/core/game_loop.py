import pygame

from engine.core import settings
from engine.ui.cursor import Cursor
from engine.ui.fps_counter import FpsCounter


class GameLoop:
    # Runs the game frame by frame: events, timing, the current screen, then the cursor
    # and FPS counter on top. Each frame is drawn on a transparent screen-sized surface,
    # then the renderer puts the world (if a screen submitted one) and that surface in
    # the window.
    def __init__(
        self,
        renderer,
        screen_size,
        state_manager,
        frame_rate,
        cursor_image=None,
        fps_setting=None,
    ):
        # What the loop drives
        self.renderer = renderer
        self.state_manager = state_manager
        self.frame_rate = frame_rate
        # The name of the setting that shows the FPS counter (None: never shown)
        self.fps_setting = fps_setting

        # The frame's surface, its timing, and the flag closing the window clears
        self.ui_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.running = True

        # Drawn cursor art replaces the system cursor, if the game has some
        self.cursor = None
        if cursor_image is not None:
            pygame.mouse.set_visible(False)
            self.cursor = Cursor(cursor_image)

        # Top right, shown while fps_setting is on
        self.fps_counter = FpsCounter(screen_size[0])

    def run(self):
        self.state_manager.get_state().enter()
        while self.running:
            self.update()
            self.draw()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Seconds since the last frame
        dt = self.clock.tick(self.frame_rate) / 1000.0

        self.state_manager.get_state().update(dt)
        if self.cursor is not None:
            self.cursor.update()
        self.fps_counter.update(dt, self.clock.get_fps())

    def draw(self):
        self.ui_surface.fill((0, 0, 0, 0))
        self.state_manager.get_state().draw(self.ui_surface)

        if self.fps_setting is not None and settings.get_setting(self.fps_setting):
            self.fps_counter.draw(self.ui_surface)
        if self.cursor is not None:
            self.cursor.draw(self.ui_surface)

        self.renderer.present(self.ui_surface)
        pygame.display.flip()
