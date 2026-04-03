"""
System: Roll Component
----------------------
Manages the player's dodge-roll mechanic, including invulnerability frames,
directional physics, and cooldown management. This component integrates with
the animation and movement systems to provide a fluid transition between
rolling and standard locomotion.

Classes:
    RollComponent: Handles state, timing, and direction for the roll action.
"""

import pygame
from Components.component import Component
from typing import Any, Dict


class RollComponent(Component):
    def __init__(self, node: Any, roll_speed: float = 0.0, cooldown: int = 800) -> None:
        """Initializes roll attributes, cooldowns, and invincibility flags."""
        super().__init__(node)
        self.is_rolling = False
        self.roll_speed = roll_speed
        self.is_invincible = False
        self.last_roll_time = 0
        self.roll_cooldown = cooldown
        self.roll_direction = pygame.Vector2(0, 0)

    def start_roll(self, dir_vector: pygame.Vector2, last_direction: str) -> None:
        """
        Initiates a roll if the cooldown has expired. Calculates direction
        based on current input or the last facing direction.
        """
        current_time = pygame.time.get_ticks()
        if (
            not self.is_rolling
            and current_time - self.last_roll_time >= self.roll_cooldown
        ):
            self.is_rolling = True
            self.is_invincible = True
            self.last_roll_time = current_time

            if dir_vector.length_squared() == 0:
                dir_map = {
                    "right": (1, 0),
                    "left": (-1, 0),
                    "up": (0, -1),
                    "down": (0, 1),
                }
                self.roll_direction = pygame.Vector2(
                    dir_map.get(last_direction, (1, 0))
                )
            else:
                self.roll_direction = dir_vector.normalize()

            if hasattr(self.node, "animations"):
                self.node.animations.change_anim(f"player_roll_{last_direction}")

    def update(self, dt: float) -> None:
        """
        Handles roll physics and animation tracking. Allows for 'animation
        canceling' near the end of the roll if movement input is detected.
        """
        if self.is_rolling:
            if hasattr(self.node, "movement"):
                vel = self.roll_direction * self.roll_speed
                self.node.movement.move(vel * dt, getattr(self.node, "wall_tiles", []))

            if hasattr(self.node, "animations"):
                controller = self.node.animations.controller
                frames = controller.animations.get(controller.current_anim, [])

                # Allow movement keys to break the roll near the end of the animation
                progress = controller.frame_index / max(1, len(frames) - 1)
                if progress > 0.8:
                    input_vec = getattr(self.node, "input_vector", pygame.Vector2(0, 0))
                    if input_vec.length_squared() > 0:
                        self.finish_roll()

                # End roll naturally on the final frame
                if controller.frame_index >= len(frames) - 1:
                    self.finish_roll()

    def finish_roll(self) -> None:
        """Resets state flags to end the roll and remove invincibility."""
        self.is_rolling = False
        self.is_invincible = False
