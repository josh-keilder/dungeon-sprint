"""
Entity: Player
--------------
The primary controllable actor. This class coordinates various logic components
(Input, Movement, Animation, Inventory) and manages the transition between
different gameplay states like walking, rolling, and idling.

Key Feature: Uses a dynamic 'stats' property to calculate real-time attributes
by combining base stats with equipment bonuses from the InventoryComponent.
"""

import pygame
from globals import *
from node import Node
from Components.healthComponent import Health, HealthBar
from Components.hitboxComponent import Hitbox
from Components.inputComponent import InputComponent
from Components.movementComponent import MovementComponent
from Components.rollComponent import RollComponent
from Components.animationComponent import AnimationComponent
from Components.inventoryComponent import InventoryComponent
from ui_objects.camera import camera


class Player(Node):
    def __init__(self, animations, pos=(0, 0), map=None):
        super().__init__()

        # --- Attributes ---
        self.name = "player"
        self.last_direction = "down"
        self.input_vector = pygame.Vector2(0, 0)
        self.walking = False
        self.pos = pygame.math.Vector2(pos)
        self.inventory_size = 20

        # Base values before equipment or status modifiers
        self.base_stats = {
            "attack": 5,
            "defense": 0,
            "speed": 70,
            "health": 500,
            "roll_speed": 200,
            "speed_multiplier": 1,
        }

        self.wall_tiles = None

        # --- Visuals & Animation ---
        self.animations = AnimationComponent(self, animations, "player_idle_down")
        self.image = animations["player_idle_down"][0]
        self.rect = self.image.get_frect()
        self.rect.center = pos

        # --- Component Composition ---
        self.health = Health(self, self.base_stats["health"])
        self.health_bar = HealthBar(
            self,
            self.base_stats["health"],
            width=200,
            height=10,
            is_player=True,
            shrink_speed=5,
        )
        self.hitbox = Hitbox(self)
        self.input = InputComponent(self, map=map)
        self.inventory = InventoryComponent(self, size=self.inventory_size)
        self.movement = MovementComponent(self, self.base_stats["speed"])
        self.roll = RollComponent(self, roll_speed=self.base_stats["roll_speed"])

    @property
    def stats(self):
        """Calculates final stats by merging base_stats with equipment bonuses."""
        final_stats = self.base_stats.copy()
        bonuses = self.inventory.get_equipment_bonuses()

        for stat, value in bonuses.items():
            if stat in final_stats:
                final_stats[stat] += value
        return final_stats

    def update(self, dt):
        """Main logic loop: Updates all sub-components and syncs state."""
        super().update(dt)

        # Dynamic speed adjustment based on boots/movement state
        if (
            self.walking
            and self.inventory.equipment_slots.get("boots")
            and self.base_stats["speed"] < 100
        ):
            self.base_stats["speed"] += 1
        if not self.walking and self.base_stats["speed"] > 70:
            self.base_stats["speed"] -= 5

        # Sync components with current calculated stats
        self.movement.max_speed = self.stats["speed"]
        self.movement.speed_multiplier = self.stats["speed_multiplier"]
        self.roll.roll_speed = self.base_stats["roll_speed"]

        if self.health.max_health != self.stats["health"]:
            self.health.max_health = self.stats["health"]

        # Component Updates
        self.input.update(dt)
        self.movement.update(dt)
        self.roll.update(dt)
        self.handle_animation_state()
        self.animations.update(dt)
        self.health_bar.update(dt)
        self.hitbox.update(dt)

        self.pos = pygame.math.Vector2(self.rect.topleft)

    def draw(self, screen, camera=None):
        """Renders the player, health bar, inventory, and debug hitbox."""
        # Render Player Sprite
        if camera:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
        else:
            screen.blit(self.image, self.rect.topleft)

        self.health_bar.draw(screen, camera)

        if self.input.show_inventory:
            self.inventory.draw(screen)

        # Debug: Collision boundary
        self.hitbox.draw(screen, camera, color=GREEN)

        super().draw(screen, camera)

    def handle_animation_state(self):
        """Determines the correct animation string based on current movement/action."""
        if getattr(self.roll, "is_rolling", False):
            action = "roll"
        elif self.walking:
            action = "walk"
        else:
            action = "idle"

        anim_name = f"player_{action}_{self.last_direction}"
        self.animations.change_anim(anim_name)
