import pygame
from globals import *
from ui_objects.camera import camera
from Entities.animations import Animations
from Entities.enemies.enemyTextureData import skull_enemy_texture_data
from Components.health import Health, HealthBar

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

        #self.health_bar, self.health_bar_rect = display_health_bar()

    def update(self, wall_tiles):
        pass

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Display the health bar above the enemy
        # self.health_bar_rect.topleft = self.rect.x - camera.x, self.rect.y - camera.y - 10
        # screen.blit(self.health_bar, (self.health_bar_rect))

class Skull_Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos=(0,0)):
        super().__init__(groups)

        # --- COMPONENTS ---
        self.health = Health(100)
        self.health_bar = HealthBar(100)
        self.animations = Animations(animations= gen_enemy_textures(skull_enemy_texture_data), start_anim= 'skull_idle', animation_speed=.1)

        # --- VISUALS / STATE ---
        self.image = self.animations.play_animation(loop=True)
        self.pos = pygame.math.Vector2(pos)
        self.rect = self.image.get_frect(topleft = self.pos)

    def update(self,wall_tiles):

        # Animation
        self.image = self.animations.play_animation(loop=True)

        # Health Bar
        self.health_bar.update(self.health.current, self.rect)

        if self.health:
            self.health.current -= 1

    def draw(self, screen):

        # Skull Enemy
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Health Bar
        self.health_bar.draw(screen, camera)