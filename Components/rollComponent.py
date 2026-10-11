import pygame
from Components.component import Component
from typing import Any
from systems.movement import move_and_collide

ROLL_DURATION = 0.4
ROLL_COOLDOWN = 1


class RollComponent(Component):
    def __init__(self, node: Any, roll_speed: float = 0.0) -> None:
        super().__init__(node)
        self.is_rolling = False
        self.roll_speed = roll_speed
        self.is_invincible = False
        self.roll_direction = pygame.Vector2(0, 0)

        self.roll_timer = 0.0
        self.cooldown_timer = 0.0

    def start_roll(self, dir_vector: pygame.Vector2) -> None:
        if dir_vector.length_squared() == 0:
            return

        if not self.is_rolling and self.cooldown_timer <= 0:
            self.is_rolling = True
            self.roll_timer = ROLL_DURATION
            self.is_invincible = True
            self.cooldown_timer = ROLL_COOLDOWN

            self.roll_direction = dir_vector.copy()

    def update(self, dt: float, walls) -> None:
        if self.is_rolling:
            displacement = self.roll_direction * self.roll_speed * dt
            hit_x, hit_y = move_and_collide(self.node.rect, displacement, walls)

            if hit_x:
                self.node.velocity.x = 0
            if hit_y:
                self.node.velocity.y = 0

            self.roll_timer -= dt

            if self.roll_timer <= 0:
                self.finish_roll()

        self.cooldown_timer -= dt

    def finish_roll(self) -> None:
        self.is_rolling = False
        self.is_invincible = False
