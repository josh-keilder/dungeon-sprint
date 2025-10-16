import pygame
import globals
from globals import *

class InputController:
    def __init__(self, player):
        self.player = player

    def handle_input(self):
        keys = pygame.key.get_pressed()
        walking = False
        player_speed = 1
        dir_x, dir_y = 0 , 0

        # Movement checks
        if keys[pygame.K_a]:
            dir_x -= player_speed; self.player.last_direction = 'left'; walking = True
        if keys[pygame.K_d]:
            dir_x += player_speed; self.player.last_direction = 'right'; walking = True
        if keys[pygame.K_w]:
            dir_y -= player_speed; self.player.last_direction = 'up'; walking = True
        if keys[pygame.K_s]:
            dir_y += player_speed; self.player.last_direction = 'down'; walking = True

        input_vector = pygame.math.Vector2(dir_x, dir_y)
        if input_vector.length() > 0:
            input_vector = input_vector.normalize()

        # Roll Check
        if keys[pygame.K_SPACE] and walking and not self.player.roll.is_rolling:
            self.player.roll.start_roll(self.player, input_vector, self.player.last_direction)


        # Debug Button
        if keys[pygame.K_p]:
            globals.DEBUG_HITBOXES = not globals.DEBUG_HITBOXES

        return input_vector, walking