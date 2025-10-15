import pygame
from globals import *

class MovementController:
    def __init__(self, speed=1):
        self.speed = speed

    def move(self, entity, dir_vector, wall_tiles):
        entity.rect.x += dir_vector.x * self.speed
        if pygame.sprite.spritecollide(entity, wall_tiles, dokill=False):
            entity.rect.x -= dir_vector.x
        entity.rect.y += dir_vector.y * self.speed
        if pygame.sprite.spritecollide(entity, wall_tiles, dokill=False):
            entity.rect.y -= dir_vector.y




class RollController:
    def __init__(self, roll_speed=4, cooldown = 3000):

        self.is_rolling = False  # Initialize our roll check as false 
        self.roll_speed = roll_speed     # how fast the roll moves
        self.is_invincible = False # Invincibility is initialized as false 
        self.last_roll_time = 0
        self.roll_cooldown = cooldown # in milliseconds
        self.roll_direction = pygame.Vector2(0,0)

        self.roll_anim = None


    def start_roll(self, entity, dir_vector, last_direction):
        current_time = pygame.time.get_ticks()
        if not self.is_rolling and current_time - self.last_roll_time >= self.roll_cooldown:
            self.is_rolling = True
            self.is_invincible = True
            self.last_roll_time = current_time
            self.roll_direction = dir_vector

            self.roll_anim = f'player_roll_{last_direction}'
            entity.animations.set_animation(self.roll_anim)