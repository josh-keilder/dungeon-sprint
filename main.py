import pygame
import sys
import os

from player import Player
from stateManager import Level, Start, GameStateManager

FPS = 60


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        
        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager)
        self.level = Level(self.screen, self.gameStateManager)
        

        self.states = {'start':self.start, 'level':self.level}

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()



            # inside of the self.states dictionary, look for the key that is returned from the get_state() method and run it
            self.states[self.gameStateManager.get_state()].run() 

            pygame.display.update()
            self.clock.tick(FPS)




if __name__ == '__main__':
    game = Game()
    game.run()

