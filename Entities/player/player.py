import pygame
from globals import *
from node import Node
from Components.healthComponent import Health, HealthBar
from Components.hitboxComponent import Hitbox
from Components.rollComponent import RollComponent
from Components.animationComponent import AnimationComponent
from Components.inventoryComponent import InventoryComponent
from ui_objects.camera import camera
from systems.consumables import use_small_health_potion
from systems.movement import steer, move_and_collide


class Player(Node):
    def __init__(self, animations, pos=(0, 0)):
        super().__init__()

        # --- Attributes ---
        self.name = "player"
        self.last_direction = "down"
        self.walking = False
        self.pos = pygame.math.Vector2(pos)
        self.inventory_size = 20

        self.velocity = pygame.Vector2()

        self.intent = {"move": pygame.Vector2(), "roll": False, "heal": False}

        # Base values before equipment or status modifiers
        self.base_stats = {
            "attack": 5,
            "defense": 0,
            "speed": 70,
            "health": 500,
            "roll_speed": 200,
            "speed_multiplier": 1,
            "acceleration": 2400,
            "friction": 3000,
        }

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
        self.inventory = InventoryComponent(self, size=self.inventory_size)
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

    def update(self, dt, walls):
        """Main logic loop: Updates all sub-components and syncs state."""
        super().update(dt)

        move = self.intent["move"]
        self.walking = move.length_squared() > 0
        if self.walking:
            self.update_facing(move)

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
        self.roll.roll_speed = self.base_stats["roll_speed"]

        if self.health.max_health != self.stats["health"]:
            self.health.max_health = self.stats["health"]

        # Component Updates
        if self.intent["roll"]:
            self.roll.start_roll(move, self.last_direction)

        if self.intent["heal"]:
            use_small_health_potion(self.health, self.inventory)

        self.update_movement(dt, walls)

        self.roll.update(dt, walls)
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
        self.animations.set_animation(anim_name)

    def update_facing(self, move):
        if move.y < 0:
            self.last_direction = "up"
        elif move.y > 0:
            self.last_direction = "down"
        elif move.x < 0:
            self.last_direction = "left"
        elif move.x > 0:
            self.last_direction = "right"

    def update_movement(self, dt, walls):
        stats = self.stats

        speed_cap = stats["speed"] * stats["speed_multiplier"]

        self.velocity = steer(
            self.velocity,
            self.intent["move"],
            stats["acceleration"],
            stats["friction"],
            speed_cap,
            dt,
        )

        hit_x, hit_y = move_and_collide(self.rect, self.velocity * dt, walls)

        if hit_x:
            self.velocity.x = 0
        if hit_y:
            self.velocity.y = 0
