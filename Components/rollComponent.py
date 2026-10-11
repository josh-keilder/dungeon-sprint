import pygame
from Components.component import Component
from typing import Any
from systems.movement import move_and_collide


class RollComponent(Component):
    def __init__(self, node: Any, roll_speed: float = 0.0, cooldown: int = 800) -> None:
        super().__init__(node)
        self.is_rolling = False
        self.roll_speed = roll_speed
        self.is_invincible = False
        self.last_roll_time = 0
        self.roll_cooldown = cooldown
        self.roll_direction = pygame.Vector2(0, 0)

    def start_roll(self, dir_vector: pygame.Vector2, last_direction: str) -> None:
        if dir_vector.length_squared() == 0:
            return

        current_time = pygame.time.get_ticks()
        if (
            not self.is_rolling
            and current_time - self.last_roll_time >= self.roll_cooldown
        ):
            self.is_rolling = True
            self.is_invincible = True
            self.last_roll_time = current_time

            self.roll_direction = dir_vector.copy()

            if hasattr(self.node, "animations"):
                self.node.animations.set_animation(f"player_roll_{last_direction}")

    def update(self, dt: float, walls) -> None:
        if self.is_rolling:

            displacement = self.roll_direction * self.roll_speed * dt
            hit_x, hit_y = move_and_collide(self.node.rect, displacement, walls)

            if hit_x:
                self.node.velocity.x = 0
            if hit_y:
                self.node.velocity.y = 0

            if hasattr(self.node, "animations"):
                animations = self.node.animations
                frames = animations.animations.get(animations.current_anim, [])

                # Allow movement keys to break the roll near the end of the animation
                progress = animations.frame_index / max(1, len(frames) - 1)
                if progress > 0.8:
                    move = self.node.intent["move"]
                    if move.length_squared() > 0:
                        self.finish_roll()

                # End roll naturally on the final frame
                if animations.frame_index >= len(frames) - 1:
                    self.finish_roll()

    def finish_roll(self) -> None:
        self.is_rolling = False
        self.is_invincible = False
