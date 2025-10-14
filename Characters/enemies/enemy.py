import pygame
from globals import *
from states.dungeons.camera import camera
from Characters.animations import Animations
from Characters.enemies.enemyTextureData import skull_enemy_texture_data

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

class Skeleton(pygame.sprite.Sprite):
    def __init__(self, groups, pos=(0,0), size=TILESIZE):
        super().__init__(groups)
        # Simple red square
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)
        self.rect = self.image.get_frect()
        self.pos = pygame.math.Vector2(pos)
        self.rect.topleft = self.pos

        self.patrolling = True

        self.health_bar = self.create_health_bar()

    def update(self, wall_tiles):
        self.patrol()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Display the health bar above the enemy
        self.health_bar_rect.topleft = self.rect.x - camera.x, self.rect.y - camera.y - 10
        screen.blit(self.health_bar, (self.health_bar_rect))

    def patrol(self):
        # Allows the enemy to patrol from one point to another UNTIL the player is close enough to be spotted
        if self.patrolling:
            if self.pos.x <= 1220:
                self.pos.x += 1
            elif self.pos.x >= 1200:
                self.pos.x -= 1
    def attack(self):
        pass
        # Enemy attacks
    def create_health_bar(self):
        # Create a green health bar image
        health_image = pygame.Surface((TILESIZE, 4))
        health_image.fill(GREEN)
        self.health_bar_rect = health_image.get_frect()

        return health_image
    

class Skull_Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos=(0,0)):
        super().__init__(groups)
        self.skull_enemy_textures = gen_enemy_textures(skull_enemy_texture_data)
        self.skull_animations = Animations(animations= self.skull_enemy_textures, start_anim= 'skull_idle', animation_speed=.1)
        self.image = self.skull_animations.play_animation(loop=True)
        self.rect = self.image.get_frect()
        self.pos = pygame.math.Vector2(pos)
        self.rect.topleft = self.pos

        self.skull_enemy_textures = gen_enemy_textures(skull_enemy_texture_data)

        self.health_bar = self.create_health_bar()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Display the health bar above the enemy
        self.health_bar_rect.topleft = self.rect.x - camera.x, self.rect.y - camera.y - 10
        screen.blit(self.health_bar, (self.health_bar_rect))

    def update(self,wall_tiles):
        self.image = self.skull_animations.play_animation(loop=True)

    def create_health_bar(self):
        # Create a green health bar image
        health_image = pygame.Surface((TILESIZE, 4))
        health_image.fill(GREEN)
        self.health_bar_rect = health_image.get_frect()

        return health_image
    
    