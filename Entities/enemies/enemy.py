import pygame
from globals import *
from ui_objects.camera import camera
from Controllers.animations import AnimationController
from Entities.enemies.enemyTextureData import skull_enemy_texture_data
from Components.health import Health, HealthBar
from Components.hitbox import Hitbox

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
    def __init__(self, groups, pos=(0,0)):
        super().__init__(groups)

        # --- VISUALS / STATE ---
        self.animations = AnimationController(animations= gen_enemy_textures(skull_enemy_texture_data), start_anim= 'skull_idle', animation_speed=.1)
        self.image = self.animations.play_animation(loop=True)
        self.pos = pygame.math.Vector2(pos)
        self.rect = self.image.get_frect(topleft = self.pos)

        # --- COMPONENTS ---
        self.health = Health(100)
        self.health_bar = HealthBar(100)
        self.hitbox = Hitbox(self)

    def update(self,wall_tiles):

        # Animation
        self.image = self.animations.play_animation(loop=True)

        # Health Bar
        self.health_bar.update(self.health.current, self.rect)

        # Hitbox
        self.hitbox.update()

    def draw(self, screen):

        # Skeleton Enemy
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Health Bar
        self.health_bar.draw(screen, camera)

        # Show Hitbox for debug
        self.hitbox.draw(screen)

class Skull_Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos=(0,0)):
        super().__init__(groups)

        # --- VISUALS / STATE ---
        self.animations = AnimationController(animations= gen_enemy_textures(skull_enemy_texture_data), start_anim= 'skull_idle', animation_speed=.1)
        self.image = self.animations.play_animation(loop=True)
        self.pos = pygame.math.Vector2(pos)
        self.rect = self.image.get_frect(topleft = self.pos)

        # --- COMPONENTS ---
        self.health = Health(100)
        self.health_bar = HealthBar(100)
        self.hitbox = Hitbox(self)

    def update(self,wall_tiles):

        # Animation
        self.image = self.animations.play_animation(loop=True)

        # Health Bar
        self.health_bar.update(self.health.current, self.rect)

        # Hitbox
        self.hitbox.update()

    def draw(self, screen):

        # Skull Enemy
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Health Bar
        self.health_bar.draw(screen, camera)

        # Show Hitbox for debug
        self.hitbox.draw(screen)