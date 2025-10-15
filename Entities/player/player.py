import pygame
from globals import *
from Controllers.animations import AnimationController
from ui_objects.camera import camera
from Components.health import Health, HealthBar
from Components.hitbox import Hitbox
from Controllers.movement import MovementController, RollController
from Controllers.input import InputController 

from ui_objects.create_outline  import create_outline

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, animations, pos = (0,0)):
        super().__init__(groups)

        # --- VISUALS ---
        self.animations = AnimationController(animations= animations, start_anim= 'player_idle_down')
        self.image = self.animations.play_animation(loop=True)
        self.rect = self.image.get_frect()
        self.rect.center = pos
        
        # --- CONTROLLERS ---
        self.movement = MovementController(speed=1)
        self.roll = RollController()
        self.input = InputController(self)

        print(self.input.handle_input())

        # --- COMPONENTS ---
        self.health = Health(max_health=100)
        self.health_bar = HealthBar(max_health=100, width=200, height=10, is_player =True)
        self.hitbox = Hitbox(self)

        # --- PLAYER ATTRIBUTES ---
        self.last_direction = 'down'

    def update(self, wall_tiles):
        input_vector, walking = self.input.handle_input()

        if self.roll.is_rolling: # Checks if the player is rolling and since it isn't a looping animation we play it separately
            self.roll.start_roll(self, input_vector, self.last_direction)
            self.movement.move(self, self.roll.roll_direction * self.roll.roll_speed, wall_tiles)  
            self.image = self.animations.play_animation(loop=False)
            frames = self.animations.animations[self.animations.current_anim]
            if self.animations.frame_index >= len(frames) - 1: # Ends the animation
                self.roll.is_rolling = False
                self.roll.is_invincible = False
        else:
            # Move when not rolling
            self.movement.move(self, input_vector, wall_tiles)
            # Walking/Idle Animations
            if walking:
                self.animations.set_animation(f'player_walk_{self.last_direction}')
            else:
                self.animations.set_animation(f'player_idle_{self.last_direction}')

        # Constantly updates whatever animation the player is currently doing
        self.image = self.animations.play_animation(loop=True)

        # Health bar
        self.health_bar.update(self.health.current, self.rect)

        # Hitbox
        self.hitbox.update()

        # Constantly updates the camera position to follow the player
        camera.y = self.rect.y - camera.height/2 + self.image.get_height()/2
        camera.x = self.rect.x - camera.height/2 + self.image.get_height()/2

    def draw(self, screen):
        # Player
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Health bar
        self.health_bar.draw(screen, camera)

        # Show Hitbox for debug
        self.hitbox.draw(screen)