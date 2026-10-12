import pygame
from globals import *
from node import Node
from Components.healthComponent import Health, HealthBar
from Components.hitboxComponent import Hitbox
from Components.animationComponent import AnimationComponent
from typing import Dict, List, Any, Optional

from systems.enemy_ai import fly_velocity, wander_chase_velocity, random_idle_direction
from systems.movement import move_and_collide

# Global cache for storing surface lists to optimize memory and performance
ENEMY_CACHE = {}


def gen_enemy_textures(texture_data: Dict[str, Any]) -> Dict[str, List[pygame.Surface]]:
    cache_key = list(texture_data.values())[0]["file_path"]

    if cache_key in ENEMY_CACHE:
        return ENEMY_CACHE[cache_key]

    textures = {}
    for name, data in texture_data.items():
        enemy_img = pygame.image.load(data["file_path"]).convert_alpha()
        w, h = data["size"]
        frames = data["frames"]
        row = data["position"][1]
        textures[name] = []

        for i in range(frames):
            x = i * w
            y = row * h
            frame = enemy_img.subsurface(pygame.Rect(x, y, w, h))
            textures[name].append(frame)

    ENEMY_CACHE[cache_key] = textures
    return textures


class Enemy(Node):
    def __init__(self, type_data, pos) -> None:
        super().__init__()
        animations = gen_enemy_textures(type_data["texture_data"])
        start_animation = type_data["start_animation"]
        self.attack_damage = type_data["attack_damage"]
        self.speed = type_data["speed"]
        self.behavior = type_data["behavior"]
        self.pos = pygame.math.Vector2(pos)

        self.animations = AnimationComponent(
            self, animations, start_animation=start_animation
        )
        self.image = animations[start_animation][0]
        self.rect = self.image.get_frect(topleft=self.pos)

        self.health = Health(self, type_data["max_health"])
        self.health_bar = HealthBar(self)
        self.hitbox = Hitbox(self)

        self.flee_timer = 0.0
        self.return_timer = 0.0
        self.idle_direction = random_idle_direction()

    def update(self, dt, walls, target_pos) -> None:
        if not self.active:
            return

        super().update(dt)
        self.animations.update(dt)
        self.health_bar.update(dt)
        self.update_movement(dt, walls, target_pos)
        self.pos.xy = self.rect.topleft
        self.hitbox.update(dt)

    def update_movement(self, dt, walls, target_pos):
        if self.behavior == "fly":
            velocity = fly_velocity(self, target_pos, dt)
            self.rect.x += velocity.x * dt
            self.rect.y += velocity.y * dt

        elif self.behavior == "wander_chase":
            velocity = wander_chase_velocity(self, target_pos, walls)
            move_and_collide(self.rect, velocity * dt, walls)

    def draw(
        self, screen: pygame.Surface, camera: Optional[pygame.Rect] = None
    ) -> None:
        if not self.active:
            return

        draw_pos = self.rect.topleft

        if camera:
            draw_pos = (self.rect.x - camera.x, self.rect.y - camera.y)

        screen.blit(self.image, draw_pos)
        self.health_bar.draw(screen, camera)
        self.hitbox.draw(screen, camera)

        super().draw(screen, camera)
