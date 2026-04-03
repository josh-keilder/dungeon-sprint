"""
System: Movement Component
--------------------------
Handles complex locomotion for both the player and AI entities. Supports
physics-based acceleration/friction for player input, as well as several
AI behaviors including flying, wandering, chasing, and fleeing. Includes
an axis-aligned collision resolution system against static wall tiles.

Classes:
    MovementComponent: The primary controller for spatial updates and AI logic.
"""

import pygame
import random
from globals import *
from Components.component import Component
from typing import Any, List, Optional


class MovementComponent(Component):
    def __init__(
        self,
        node: Any,
        speed: float = 100.0,
        behavior: str = "basic",
        player: Optional[Any] = None,
    ) -> None:
        """Initializes movement physics, AI timers, and behavioral settings."""
        super().__init__(node)
        self.node = node
        self.max_speed = speed

        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = 2400
        self.friction = 3000
        self.speed_multiplier = 1.0

        self.flying = False
        self.behavior = behavior
        self.player = player
        self.flee_timer = 0.0
        self.return_timer = 0.0
        self.idle_direction = pygame.math.Vector2(
            random.choice([-1, 1]), random.choice([-1, 1])
        )

    def update(self, dt: float = 0.0) -> None:
        """
        Main update entry point. Switches between AI behaviors or processes
        standard physics-based movement for player-controlled nodes.
        """
        if self.behavior == "fly" and self.player:
            self.fly_behavior(dt)
        elif self.behavior == "wander_chase" and self.player:
            self.wander_chase_behavior(dt)
        else:
            if hasattr(self.node, "input_vector"):
                target_dir = self.node.input_vector

                if target_dir.length_squared() > 0:
                    if target_dir.length_squared() > 1:
                        target_dir.normalize_ip()

                    # Apply extra friction when making sharp turns or reversing
                    if (
                        self.velocity.length_squared() > 0
                        and target_dir.dot(self.velocity.normalize()) < -0.5
                    ):
                        self.velocity -= self.velocity * self.friction * 0.01 * dt

                    self.velocity += target_dir * self.acceleration * dt
                else:
                    # Apply friction/drag when no input is provided
                    if self.velocity.length_squared() > 0:
                        drag_multiplier = 1.2
                        friction_vec = (
                            self.velocity.normalize()
                            * (self.friction * drag_multiplier)
                            * dt
                        )
                        if (
                            self.velocity.length_squared()
                            < friction_vec.length_squared()
                        ):
                            self.velocity.update(0, 0)
                        else:
                            self.velocity -= friction_vec

                current_limit = self.max_speed * self.speed_multiplier
                if self.velocity.length_squared() > current_limit**2:
                    self.velocity.scale_to_length(current_limit)

                wall_tiles = getattr(self.node, "wall_tiles", [])
                self.move(self.velocity * dt, wall_tiles)

    def fly_behavior(self, dt: float) -> None:
        """AI behavior for flying entities that bypasses wall collision checks."""
        distance = self.node.pos.distance_to(self.player.pos)

        if self.flee_timer > 0:
            self.flee_timer -= dt
            dir_vector = (self.node.pos - self.player.pos).normalize() * self.max_speed
        elif self.return_timer > 0:
            self.return_timer -= dt
            dir_vector = (self.player.pos - self.node.pos).normalize() * self.max_speed
        elif distance < 200:
            dir_vector = (self.player.pos - self.node.pos).normalize() * self.max_speed
        else:
            if random.random() < 0.01:
                self.idle_direction = pygame.math.Vector2(
                    random.choice([-1, 1]), random.choice([-1, 1])
                )
            dir_vector = self.idle_direction * self.max_speed * 0.2

        self.node.rect.x += dir_vector.x * dt
        self.node.rect.y += dir_vector.y * dt
        self.node.pos.xy = self.node.rect.topleft

    def wander_chase_behavior(self, dt: float) -> None:
        """AI behavior that chases the player if in sight, otherwise wanders."""
        if self.has_line_of_sight():
            dir_vector = (self.player.pos - self.node.pos).normalize() * self.max_speed
        else:
            if random.random() < 0.01:
                self.idle_direction = pygame.math.Vector2(
                    random.choice([-1, 1]), random.choice([-1, 1])
                )
            dir_vector = self.idle_direction * self.max_speed * 0.5

        wall_tiles = getattr(self.node, "wall_tiles", [])
        self.move(dir_vector * dt, wall_tiles)

    def trigger_flee(self) -> None:
        """Forces the entity into a flee-then-return state cycle."""
        self.flee_timer = 2.0
        self.return_timer = 3.0

    def has_line_of_sight(self) -> bool:
        """Checks if a direct line exists between entity and player without wall obstruction."""
        if not self.player or not hasattr(self.node, "wall_tiles"):
            return False

        start = self.node.pos
        end = self.player.pos

        search_rect = pygame.Rect(
            min(start.x, end.x),
            min(start.y, end.y),
            abs(start.x - end.x),
            abs(start.y - end.y),
        ).inflate(64, 64)

        for wall in self.node.wall_tiles:
            if not search_rect.colliderect(wall.rect):
                continue
            if wall.rect.clipline(start, end):
                return False
        return True

    def move(self, dir_vector: pygame.math.Vector2, wall_tiles: List[Any]) -> None:
        """Resolves X and Y movement independently with axis-aligned collision detection."""
        if dir_vector.x == 0 and dir_vector.y == 0:
            return

        # X-Axis movement and collision
        self.node.rect.x += dir_vector.x
        if wall_tiles and not self.flying:
            for wall in wall_tiles:
                if abs(self.node.pos.x - wall.rect.centerx) > 64:
                    continue
                if self.node.rect.colliderect(wall.rect):
                    if dir_vector.x > 0:
                        self.node.rect.right = wall.rect.left
                    if dir_vector.x < 0:
                        self.node.rect.left = wall.rect.right
                    self.velocity.x = 0
                    break

        # Y-Axis movement and collision
        self.node.rect.y += dir_vector.y
        if wall_tiles and not self.flying:
            for wall in wall_tiles:
                if abs(self.node.pos.y - wall.rect.centery) > 64:
                    continue
                if self.node.rect.colliderect(wall.rect):
                    if dir_vector.y > 0:
                        self.node.rect.bottom = wall.rect.top
                    if dir_vector.y < 0:
                        self.node.rect.top = wall.rect.bottom
                    self.velocity.y = 0
                    break

        self.node.pos.xy = self.node.rect.topleft
