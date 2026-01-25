import pygame
from globals import *
from node import Node
from Components.healthComponent import Health, HealthBar
from Components.hitboxComponent import Hitbox
from Components.inputComponent import InputComponent
from Components.movementComponent import MovementComponent
from Components.rollComponent import RollComponent
from Components.animationComponent import AnimationComponent
from Components.inventoryComponent import InventoryComponent
from ui_objects.camera import camera

class Player(Node):
    def __init__(self, animations, pos=(0,0), map = None):
        super().__init__()

        # --- ATTRIBUTES ---
        self.name = 'player'
        self.max_health = 500
        self.last_direction = 'down'
        self.input_vector = pygame.Vector2(0,0)
        self.walking = False
        self.wall_tiles = None  
        self.pos = pygame.math.Vector2(pos)

        # --- VISUALS ---
        self.animations = AnimationComponent(self, animations, 'player_idle_down')
        self.image = self.animations.controller.play_animation(loop=True)
        self.rect = self.image.get_frect()
        self.rect.center = pos
        
        # --- COMPONENTS ---
        self.health = Health(self, self.max_health)
        self.health_bar = HealthBar(self, self.max_health, width=200, height=10, is_player=True, shrink_speed=5)
        self.hitbox = Hitbox(self)
        self.input = InputComponent(self, map=map)
        self.inventory = InventoryComponent(self, size=20)
        self.movement = MovementComponent(self, speed=1)
        self.roll = RollComponent(self, roll_speed=3)

    def update(self, dt):
        super().update(dt)
        
        # Update components
        self.input.update(dt)
        self.movement.update(dt)
        self.roll.update(dt)
        self.animations.update(dt)
        self.health_bar.update(dt)
        self.hitbox.update(dt)

        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Constantly updates the camera position to follow the player
        camera.y = self.rect.y - camera.height/2 + self.image.get_height()/2
        camera.x = self.rect.x - camera.height/2 + self.image.get_height()/2

    def draw(self, screen, camera=None):
        # Player
        if camera:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
        else:
            screen.blit(self.image, self.rect.topleft)

        # Health bar
        self.health_bar.draw(screen, camera)

        if self.input.show_inventory:
            self.inventory.draw(screen)

        # Show Hitbox for debug
        self.hitbox.draw(screen, camera, color=GREEN)

        super().draw(screen, camera)