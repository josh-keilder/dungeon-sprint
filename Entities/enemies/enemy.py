import pygame
from globals import *
from node import Node
from Entities.enemies.enemyTextureData import skull_enemy_texture_data
from Components.healthComponent import Health, HealthBar
from Components.hitboxComponent import Hitbox
from Components.animationComponent import AnimationComponent
from typing import Dict, List, Any, Tuple, Optional

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
    def __init__(
        self,
        animations: Dict[str, List[pygame.Surface]],
        pos: Tuple[float, float] = (0, 0),
        max_health: int = 100,
        attack_damage: int = 5,
        movement_behavior: Optional[str] = None,
        start_animation: Optional[str] = None,
        speed: int = 50,
    ) -> None:
        super().__init__()
        self.max_health = max_health
        self.attack_damage = attack_damage
        self.pos = pygame.math.Vector2(pos)

        self.animations = AnimationComponent(
            self, animations, start_animation=start_animation
        )
        self.image = animations[start_animation][0]
        self.rect = self.image.get_frect(topleft=self.pos)

        self.health = Health(self, self.max_health)
        self.health_bar = HealthBar(self)
        self.hitbox = Hitbox(self)

        self.speed = speed
        self.behavior = movement_behavior
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


class Skeleton(Enemy):
    def __init__(self, pos: Tuple[float, float] = (0, 0)) -> None:
        textures = gen_enemy_textures(skull_enemy_texture_data)
        super().__init__(
            textures,
            pos,
            max_health=100,
            attack_damage=3,
            movement_behavior="wander_chase",
            start_animation="skull_idle",
            speed=40,
        )


class Skull_Enemy(Enemy):
    def __init__(self, pos: Tuple[float, float] = (0, 0)) -> None:
        textures = gen_enemy_textures(skull_enemy_texture_data)
        super().__init__(
            textures,
            pos,
            max_health=100,
            attack_damage=5,
            movement_behavior="fly",
            start_animation="skull_idle",
            speed=50,
        )
