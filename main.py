import pygame
from globals import *

from states.stateManager import GameStateManager
from states.start import Start
from states.options import Options
from states.dungeons.camera import create_screen
from states.cursor import Cursor

class Game:
    def __init__(self):
        pygame.init()
        # The screen is created within the camera module to allow a player following camera
        self.screen = create_screen(SCREENWIDTH, SCREENHEIGHT, "Dungeon Sprint")
        self.clock = pygame.time.Clock()
        self.running = True


        pygame.mouse.set_visible(False)
        self.cursor_img = pygame.image.load("Assets/Cursors/01.png").convert_alpha()
        self.cursor = Cursor(self.screen, self.cursor_img)
        
        # Allows the game to change from different states(menus/levels) and automatically sets it to our start screen first and creates the start and options screen right away
        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager, self.cursor)
        self.options = Options(self.screen, self.gameStateManager, self.cursor)
        self.gameStateManager.add_state('options', self.options)
        self.gameStateManager.add_state('start', self.start)

    def run(self):
            while self.running:
                 self.update()
                 self.draw()

    def update(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

        # Updates current state
        self.gameStateManager.get_state().update()
        # print(self.gameStateManager.all_states()) # Check states

        self.cursor.update()

        pygame.display.update()
        self.clock.tick(FRAMERATE)

    def draw(self):
        # Clears the screen so theres no duplicate sprites
        self.screen.fill(CLEAR)

        # Draws the current state
        self.gameStateManager.get_state().draw()

        self.cursor.draw()

if __name__ == '__main__':
    game = Game()
    game.run()