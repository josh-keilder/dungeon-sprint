import pygame
from globals import *
from node import Node
from Components.healthComponent import Health, HealthBar
from Components.hitboxComponent import Hitbox
from Components.animationComponent import AnimationComponent
from Components.inventoryComponent import InventoryComponent
from ui_objects.camera import camera
from systems.consumables import use_small_health_potion
from systems.movement import steer, move_and_collide
from systems.roll import try_start_roll, advance_roll
from systems.stats import compute_stats, update_speed_ramp


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
        self.speed_ramp = 0.0

        self.intent = {"move": pygame.Vector2(), "roll": False, "heal": False}

        # Base values before equipment or status modifiers
        self.base_stats = {
            "attack": 5,
            "defense": 0,
            "max_speed": 70,
            "health": 500,
            "roll_speed": 200,
            "acceleration": 2400,
            "friction": 3000,
        }

        self.roll = {
            "active": False,
            "direction": pygame.Vector2(),
            "timer": 0.0,
            "cooldown": 0.0,
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

        self.stats = compute_stats(
            self.base_stats, self.inventory.equipment_slots.values()
        )

    def update(self, dt, walls):
        """Main logic loop: Updates all sub-components and syncs state."""
        super().update(dt)

        move = self.intent["move"]
        self.walking = move.length_squared() > 0
        if self.walking:
            self.update_facing(move)

        # Dynamic speed adjustment based on boots/movement state
        building = (
            self.walking and self.inventory.equipment_slots.get("boots") is not None
        )
        self.speed_ramp = update_speed_ramp(self.speed_ramp, building, dt)

        self.stats = compute_stats(
            self.base_stats, self.inventory.equipment_slots.values()
        )
        self.stats["max_speed"] += self.speed_ramp

        if self.health.max_health != self.stats["health"]:
            self.health.max_health = self.stats["health"]

        # Component Updates
        if self.intent["roll"]:
            try_start_roll(self.roll, move)

        if self.intent["heal"]:
            use_small_health_potion(self.health, self.inventory)

        self.update_movement(dt, walls)
        self.update_roll(dt, walls)

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
        if self.roll["active"]:
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
        self.velocity = steer(
            self.velocity,
            self.intent["move"],
            self.stats["acceleration"],
            self.stats["friction"],
            self.stats["max_speed"],
            dt,
        )

        hit_x, hit_y = move_and_collide(self.rect, self.velocity * dt, walls)

        if hit_x:
            self.velocity.x = 0
        if hit_y:
            self.velocity.y = 0

    def update_roll(self, dt, walls):
        if self.roll["active"]:
            displacement = self.roll["direction"] * self.stats["roll_speed"] * dt

            hit_x, hit_y = move_and_collide(self.rect, displacement, walls)

            if hit_x:
                self.velocity.x = 0
            if hit_y:
                self.velocity.y = 0

        advance_roll(self.roll, dt)
