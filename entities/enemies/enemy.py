import pygame

from globals import RED, TILE_SIZE
from systems import debug
from systems.animation import advance_animation, new_animation
from systems.assets import load_animations
from systems.blink import is_blink_hidden
from systems.enemy_ai import fly_velocity, random_idle_direction, wander_chase_velocity
from systems.health import new_health
from systems.hitbox import draw_hitbox
from systems.movement import decay_velocity, move_and_collide
from systems.timer import advance_timer, new_timer
from ui_components.health_bar import draw_health_bar

ENEMY_HEALTH_BAR_WIDTH = TILE_SIZE
ENEMY_HEALTH_BAR_HEIGHT = 4
ENEMY_HEALTH_BAR_GAP = 8


class Enemy:
    def __init__(self, type_data, pos):
        animations = load_animations(type_data["texture_data"])
        start_animation = type_data["start_animation"]

        self.attack_damage = type_data["attack_damage"]
        self.speed = type_data["speed"]
        self.knockback_multiplier = type_data["knockback_multiplier"]
        self.knockback_decay_rate = type_data["knockback_decay_rate"]
        self.blink_interval = type_data["blink_interval"]
        self.invulnerability_duration = type_data["invulnerability_duration"]

        self.behavior = type_data["behavior"]
        self.pos = pygame.math.Vector2(pos)

        self.animation = new_animation(animations, start_animation)
        self.image = animations[start_animation][0]
        self.rect = self.image.get_frect(topleft=self.pos)

        self.health = new_health(type_data["max_health"])

        self.invulnerability = new_timer()

        self.flee_timer = 0.0
        self.return_timer = 0.0
        self.idle_direction = random_idle_direction()

        self.knockback_velocity = pygame.Vector2()

    def update(self, dt, walls, target_pos):
        self.image = advance_animation(self.animation, dt)
        self.update_movement(dt, walls, target_pos)
        self.update_knockback(dt, walls)
        advance_timer(self.invulnerability, dt)
        self.pos.xy = self.rect.topleft

    def update_movement(self, dt, walls, target_pos):
        if self.behavior == "fly":
            velocity = fly_velocity(self, target_pos, dt)
            self.rect.x += velocity.x * dt
            self.rect.y += velocity.y * dt

        elif self.behavior == "wander_chase":
            velocity = wander_chase_velocity(self, target_pos, walls)
            move_and_collide(self.rect, velocity * dt, walls)

    def update_knockback(self, dt, walls):
        hit_x, hit_y = move_and_collide(self.rect, self.knockback_velocity * dt, walls)

        if hit_x:
            self.knockback_velocity.x = 0
        if hit_y:
            self.knockback_velocity.y = 0

        self.knockback_velocity = decay_velocity(
            self.knockback_velocity, self.knockback_decay_rate, dt
        )

    def draw(self, screen, camera=None):
        blink_hidden = is_blink_hidden(self.invulnerability, self.blink_interval)

        draw_pos = self.rect.topleft

        if camera:
            draw_pos = (self.rect.x - camera.x, self.rect.y - camera.y)

        if not blink_hidden:
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
