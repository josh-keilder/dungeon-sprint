import pygame
from globals import *
from systems.health import new_health
from typing import Optional
from ui_objects.health_bar import draw_health_bar
from systems.animation import new_animation, advance_animation
from systems.enemy_ai import fly_velocity, wander_chase_velocity, random_idle_direction
from systems.movement import move_and_collide
from systems.assets import load_animations
from systems.hitbox import draw_hitbox
from systems import debug

ENEMY_HEALTH_BAR_WIDTH = TILESIZE
ENEMY_HEALTH_BAR_HEIGHT = 4
ENEMY_HEALTH_BAR_GAP = 8


class Enemy:
    def __init__(self, type_data, pos) -> None:
        animations = load_animations(type_data["texture_data"])
        start_animation = type_data["start_animation"]
        self.attack_damage = type_data["attack_damage"]
        self.speed = type_data["speed"]
        self.behavior = type_data["behavior"]
        self.pos = pygame.math.Vector2(pos)

        self.animation = new_animation(animations, start_animation)
        self.image = animations[start_animation][0]
        self.rect = self.image.get_frect(topleft=self.pos)

        self.health = new_health(type_data["max_health"])

        self.flee_timer = 0.0
        self.return_timer = 0.0
        self.idle_direction = random_idle_direction()

    def update(self, dt, walls, target_pos) -> None:

        self.image = advance_animation(self.animation, dt)
        self.update_movement(dt, walls, target_pos)
        self.pos.xy = self.rect.topleft

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

        draw_pos = self.rect.topleft

        if camera:
            draw_pos = (self.rect.x - camera.x, self.rect.y - camera.y)

        screen.blit(self.image, draw_pos)

        if self.health["current"] < self.health["max_health"]:
            bar_x = self.rect.centerx - ENEMY_HEALTH_BAR_WIDTH // 2
            bar_y = self.rect.top - ENEMY_HEALTH_BAR_GAP

            bar_pos = (bar_x, bar_y)
            if camera:
                bar_pos = (bar_x - camera.x, bar_y - camera.y)

            draw_health_bar(
                screen,
                self.health,
                *bar_pos,
                ENEMY_HEALTH_BAR_WIDTH,
                ENEMY_HEALTH_BAR_HEIGHT
            )

        if debug.show_hitboxes:
            draw_hitbox(screen, self.image, self.rect, camera, RED)
