import pygame
from globals import *
from Entities.animations import Animations
from ui_objects.camera import camera
from Components.health import Health, HealthBar
from Components.movement import MovementController, RollController

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, animations, pos = (0,0)):
        super().__init__(groups)

        # --- VISUALS ---
        self.animations = Animations(animations= animations, start_anim= 'player_idle_down')
        self.image = self.animations.play_animation(loop=True)
        self.rect = self.image.get_frect()
        self.rect.center = pos
        
        # --- CONTROLLERS ---
        self.movement = MovementController(speed=1)
        self.roll = RollController()
        # self.input = input()

        # --- COMPONENTS ---
        self.health = Health(100)
        self.health_bar = HealthBar(100, is_player =True)

        # --- PLAYER ATTRIBUTES ---
        self.last_direction = 'down'

    def input(self):
        keys = pygame.key.get_pressed()
        walking = False
        player_speed = 1
        dir_x, dir_y = 0 , 0

        # Movement checks
        if keys[pygame.K_a]:
            dir_x -= player_speed; self.last_direction = 'left'; walking = True
        if keys[pygame.K_d]:
            dir_x += player_speed; self.last_direction = 'right'; walking = True
        if keys[pygame.K_w]:
            dir_y -= player_speed; self.last_direction = 'up'; walking = True
        if keys[pygame.K_s]:
            dir_y += player_speed; self.last_direction = 'down'; walking = True

        input_vector = pygame.math.Vector2(dir_x, dir_y)
        if input_vector.length() > 0:
            input_vector = input_vector.normalize()

        # Roll Check
        if keys[pygame.K_SPACE] and walking and not self.roll.is_rolling:
            self.roll.start_roll(self, input_vector, self.last_direction)

        return input_vector, walking

    def update(self, wall_tiles):
        input_vector, walking = self.input()

        if self.roll.is_rolling: # Checks if the player is rolling and since it isn't a looping animation we play it separately
            self.roll.start_roll(self, input_vector, self.last_direction)
            self.movement.move(self, self.roll.roll_direction * self.roll.roll_speed, wall_tiles)  
            self.image = self.animations.play_animation(loop=False)
            frames = self.animations.animations[self.animations.current_anim]
            if self.animations.frame_index >= len(frames) - 1:
                self.roll.is_rolling = False
                self.roll.is_invincible = False
        else:
            # Move when not rolling
            self.movement.move(self, input_vector, wall_tiles)
            # --- Walking/Idle Animations ---
            if walking:
                self.animations.set_animation(f'player_walk_{self.last_direction}')
            else:
                self.animations.set_animation(f'player_idle_{self.last_direction}')

        # Constantly updates whatever animation the player is currently doing
        self.image = self.animations.play_animation(loop=True)

        # Constantly updates the camera position to follow the player
        camera.y = self.rect.y - camera.height/2 + self.image.get_height()/2
        camera.x = self.rect.x - camera.height/2 + self.image.get_height()/2

    def draw(self, screen):
        # Draws the player based on the camera offset
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))