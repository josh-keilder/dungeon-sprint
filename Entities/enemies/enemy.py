"""
System: Enemy Base and Entities
-------------------------------
Defines the base Enemy class and specific enemy implementations. Includes
a texture caching system to prevent redundant surface loading and
integrates multiple components for health, hitboxes, animation, and AI-driven
movement.

Functions:
    gen_enemy_textures: Loads, slices, and caches sprite sheets based on texture data.

Classes:
    Enemy: The abstract base class for all hostile NPCs.
    Skeleton: A specific enemy type with ground-based movement behaviors.
    Skull_Enemy: A specific enemy type with flying movement behaviors.
"""

import pygame
from globals import *
from node import Node
from Entities.enemies.enemyTextureData import skull_enemy_texture_data
from Components.healthComponent import Health, HealthBar
from Components.hitboxComponent import Hitbox
from Components.animationComponent import AnimationComponent
from Components.movementComponent import MovementComponent
from typing import Dict, List, Any, Tuple, Optional

# Global cache for storing surface lists to optimize memory and performance
ENEMY_CACHE = {}


def gen_enemy_textures(texture_data: Dict[str, Any]) -> Dict[str, List[pygame.Surface]]:
    """
    Loads an enemy sprite sheet and slices it into a list of animation frames.
    Uses a global cache to avoid reloading the same file multiple times.

    Args:
        texture_data (Dict[str, Any]): Dictionary containing file paths, sizes, and frames.

    Returns:
        Dict[str, List[pygame.Surface]]: A dictionary mapping animation names to frame lists.
    """
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
        player: Optional[Any] = None,
        start_anim: Optional[str] = None,
        speed: int = 50,
    ) -> None:
        """
        Initializes the base enemy with necessary components and visual data.

        Args:
            animations (Dict[str, List[pygame.Surface]]): Sliced texture frames.
            pos (Tuple[float, float]): Initial world position.
            max_health (int): Maximum health points.
            attack_damage (int): Damage dealt to the player on collision.
            movement_behavior (Optional[str]): Key for AI behavior pattern.
            player (Optional[Any]): Reference to the player for tracking.
            start_anim (Optional[str]): Key for the initial animation state.
            speed (int): Movement speed in pixels per second.
        """
        super().__init__()
        self.max_health = max_health
        self.attack_damage = attack_damage
        self.pos = pygame.math.Vector2(pos)
        self.wall_tiles = None

        self.animations = AnimationComponent(self, animations, start_anim=start_anim)
        self.image = animations[start_anim][0]
        self.rect = self.image.get_frect(topleft=self.pos)

        self.health = Health(self, self.max_health)
        self.health_bar = HealthBar(self, self.max_health)
        self.hitbox = Hitbox(self)
        self.movement_component = MovementComponent(
            self, speed=speed, behavior=movement_behavior, player=player
        )

    def update(self, dt: float = 0) -> None:
        """
        Updates AI, animation frames, health UI, and physics collisions.

        Args:
            dt (float): Delta time since the last frame.
        """
        if not self.active:
            return

        super().update(dt)
        self.animations.update(dt)
        self.health_bar.update(dt)
        self.hitbox.update(dt)
        self.movement_component.update(dt)

        self.pos.xy = self.rect.topleft

    def draw(
        self, screen: pygame.Surface, camera: Optional[pygame.Rect] = None
    ) -> None:
        """
        Renders the enemy sprite and associated UI components to the screen.

        Args:
            screen (pygame.Surface): Surface to render on.
            camera (Optional[pygame.Rect]): Camera rect for world-to-screen conversion.
        """
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
    def __init__(
        self, pos: Tuple[float, float] = (0, 0), player: Optional[Any] = None
    ) -> None:
        """Initializes a Skeleton enemy with ground-based wander/chase behavior."""
        textures = gen_enemy_textures(skull_enemy_texture_data)
        super().__init__(
            textures,
            pos,
            max_health=100,
            attack_damage=3,
            movement_behavior="wander_chase",
            player=player,
            start_anim="skull_idle",
            speed=40,
        )


class Skull_Enemy(Enemy):
    def __init__(
        self, pos: Tuple[float, float] = (0, 0), player: Optional[Any] = None
    ) -> None:
        """Initializes a flying Skull enemy with specialized flight movement."""
        textures = gen_enemy_textures(skull_enemy_texture_data)
        super().__init__(
            textures,
            pos,
            max_health=100,
            attack_damage=5,
            movement_behavior="fly",
            player=player,
            start_anim="skull_idle",
            speed=50,
        )
        self.movement_component.flying = True
