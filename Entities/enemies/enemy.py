import pygame
from globals import *
from node import Node
from Entities.enemies.enemyTextureData import skull_enemy_texture_data
from Components.healthComponent import Health, HealthBar
from Components.hitboxComponent import Hitbox
from Components.animationComponent import AnimationComponent
from Components.movementComponent import MovementComponent

# Texture loader
def gen_enemy_textures(texture_data) -> dict:
        textures = {}

        for name, data in texture_data.items():
            enemy_img = pygame.image.load(data['file_path']).convert_alpha()
            w, h = data['size'] # unpacks the size tuple
            frames = data['frames']
            row = data['position'][1]
            textures[name] = []

            for i in range(frames):
                x = i * w
                y = row * h
                frame = enemy_img.subsurface(pygame.Rect(x, y, w, h))

                textures[name].append(frame)
        return textures

# Base Enemy class
class Enemy(Node):
    def __init__(self, animations, pos=(0,0), max_health=100, attack_damage=5, movement_behavior=None, player= None):
        super().__init__()
        self.max_health = max_health
        self.attack_damage = attack_damage
        self.pos = pos
        self.wall_tiles = None 

        # --- VISUALS / STATE ---
        self.animations = AnimationComponent(self, animations, 'skull_idle')
        self.image = self.animations.controller.play_animation(loop=True)
        self.pos = pygame.math.Vector2(pos)
        self.rect = self.image.get_frect(topleft=self.pos)

        # --- COMPONENTS ---
        self.health = Health(self, self.max_health)
        self.health_bar = HealthBar(self, self.max_health)
        self.hitbox = Hitbox(self)
        self.movement_component = MovementComponent(self, speed=1, behavior=movement_behavior, player=player)

    def update(self, dt=0):
        super().update(dt)
        # Animation
        self.animations.update(dt)

        # Health Bar
        self.health_bar.update(dt)

        # Hitbox
        self.hitbox.update(dt)

        self.movement_component.update(dt)

        self.pos = pygame.math.Vector2(self.rect.topleft)

    def draw(self, screen, camera=None):
        if camera:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
        else:
            screen.blit(self.image, self.rect.topleft)

        # Health Bar
        self.health_bar.draw(screen, camera)

        # Show Hitbox for debug
        self.hitbox.draw(screen, camera)

        super().draw(screen, camera)

# Skeleton Enemy
class Skeleton(Enemy):
    def __init__(self, pos=(0,0), player=None):
        super().__init__(gen_enemy_textures(skull_enemy_texture_data), pos, max_health=100, attack_damage=3, movement_behavior='wander_chase',player=player)

        self.movement_component.speed = 40

# Skull Enemy
class Skull_Enemy(Enemy):
    def __init__(self, pos=(0,0), player=None):
        super().__init__(gen_enemy_textures(skull_enemy_texture_data), pos, max_health=100, attack_damage=5, movement_behavior='fly', player=player)

        
        self.movement_component.flying = True
        self.movement_component.speed = 50