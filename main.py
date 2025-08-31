import pygame
import sys

from settings import *
from player import *
from stateManager import Level, Start, GameStateManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.clock = pygame.time.Clock()

        self.running = True
        
        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager)
        self.level = Level(self.screen, self.gameStateManager)
        

        self.states = {'start':self.start, 'level':self.level}
    def run(self):
            while self.running:
                 self.update()
                 self.draw()
    def update(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

        pygame.display.update()
        self.clock.tick(FRAMERATE)
    def draw(self):
        # inside of the self.states dictionary, look for the key that is returned from the get_state() method and run it
        self.states[self.gameStateManager.get_state()].run()
    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()

