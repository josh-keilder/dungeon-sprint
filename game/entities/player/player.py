import pygame

from engine.core import debug
from engine.core.timer import advance_timer, new_timer
from engine.gameplay.health import new_health, set_max_health
from engine.gameplay.inventory import new_inventory
from engine.gameplay.stats import compute_stats
from engine.graphics.animation import advance_animation, new_animation, set_animation
from engine.graphics.blink import is_blink_hidden
from engine.graphics.camera import world_to_screen
from engine.graphics.masks import draw_hitbox
from engine.io.sound import play_sfx
from engine.physics.movement import move_and_collide, move_knockback, steer
from game.data.palette import GREEN
from game.rules.consumables import use_small_health_potion
from game.rules.roll import (
    advance_roll,
    is_rolling,
    roll_speed_multiplier,
    try_start_roll,
)


class Player:
    def __init__(self, player_data, animations, center=(0, 0)):
        # Values from the player data (PLAYER_DATA)
        self.base_stats = dict(player_data["base_stats"])
        self.invulnerability_duration = player_data["invulnerability_duration"]
        self.blink_interval = player_data["blink_interval"]
        self.knockback_speed = player_data["knockback_speed"]
        self.knockback_decay_rate = player_data["knockback_decay_rate"]
        inventory_slot_count = player_data["inventory_slot_count"]
        equipment_slot_names = player_data["equipment_slot_names"]

        # Facing and movement
        self.facing = "down"
        self.walking = False
        self.velocity = pygame.Vector2()
        self.speed = 0.0  # pixels per second, measured each frame
        self.knockback_velocity = pygame.Vector2()

        # What the player asked for this frame, set by the run from input
        self.intent = {"move": pygame.Vector2(), "roll": False, "heal": False}

        # Roll, and the hit and heal timers
        self.roll = {
            "direction": pygame.Vector2(),
            "active_timer": new_timer(),
            "cooldown_timer": new_timer(),
        }
        self.invulnerability = new_timer()
        self.heal_cooldown = new_timer()

        # Animation and sprite
        self.animation = new_animation(animations, "player_idle_down")
        self.image = animations["player_idle_down"][0]
        self.rect = self.image.get_frect()
        self.rect.center = center
        self.alpha = 255  # lowered by the run during the death fade

        # Health, inventory, and stats
        self.health = new_health(self.base_stats["health"])
        self.inventory = new_inventory(inventory_slot_count, equipment_slot_names)
        self.stats = compute_stats(
            self.base_stats, self.inventory["equipment"].values()
        )

    def update(self, dt, walls):
        # Where the player starts this frame, to measure the speed afterwards
        start_pos = pygame.Vector2(self.rect.center)

        move_direction = self.intent["move"]
        self.walking = move_direction.length_squared() > 0
        if self.walking and not is_rolling(self.roll):
            self.update_facing(move_direction)

        self.stats = compute_stats(
            self.base_stats, self.inventory["equipment"].values()
        )

        if self.health["maximum"] != self.stats["health"]:
            set_max_health(self.health, self.stats["health"])

        # Actions requested this frame
        if self.intent["roll"]:
            try_start_roll(self.roll, move_direction)

        if self.intent["heal"]:
            healed = use_small_health_potion(
                self.health, self.inventory, self.heal_cooldown
            )
            if healed:
                play_sfx("heal")

        self.update_movement(dt, walls)
        self.update_roll(dt, walls)
        self.update_knockback(dt, walls)

        # Speed = how far the player actually moved this frame, after walls
        distance_moved = pygame.Vector2(self.rect.center).distance_to(start_pos)
        self.speed = distance_moved / dt

        advance_timer(self.invulnerability, dt)
        advance_timer(self.heal_cooldown, dt)

        self.update_animation()
        self.image = advance_animation(self.animation, dt)

    def draw(self, screen, camera):
        blink_hidden = is_blink_hidden(self.invulnerability, self.blink_interval)

        if not blink_hidden:
            image_to_draw = self.image
            if self.alpha < 255:
                image_to_draw = self.image.copy()
                image_to_draw.set_alpha(self.alpha)

            screen.blit(image_to_draw, world_to_screen(camera, self.rect.topleft))

        if debug.show_hitboxes:
            draw_hitbox(screen, self.image, self.rect, camera, GREEN)

    def update_facing(self, move_direction):
        if move_direction.y < 0:
            self.facing = "up"
        elif move_direction.y > 0:
            self.facing = "down"
        elif move_direction.x < 0:
            self.facing = "left"
        elif move_direction.x > 0:
            self.facing = "right"

    def update_movement(self, dt, walls):
        self.velocity = steer(
            self.velocity,
            self.intent["move"],
            self.stats["max_speed"],
            self.stats["acceleration_rate"],
            self.stats["deceleration_rate"],
            self.stats["grip"],
            dt,
        )

        hit_x, hit_y = move_and_collide(self.rect, self.velocity * dt, walls)

        if hit_x:
            self.velocity.x = 0
        if hit_y:
            self.velocity.y = 0

    def update_roll(self, dt, walls):
        if is_rolling(self.roll):
            displacement = (
                self.roll["direction"]
                * self.stats["roll_speed"]
                * roll_speed_multiplier(self.roll)
                * dt
            )

            hit_x, hit_y = move_and_collide(self.rect, displacement, walls)

            if hit_x:
                self.velocity.x = 0
            if hit_y:
                self.velocity.y = 0

        advance_roll(self.roll, dt)

    def update_knockback(self, dt, walls):
        self.knockback_velocity = move_knockback(
            self.rect, self.knockback_velocity, self.knockback_decay_rate, walls, dt
        )

    def update_animation(self):
        if is_rolling(self.roll):
            action = "roll"
        elif self.walking:
            action = "walk"
        else:
            action = "idle"

        animation_name = f"player_{action}_{self.facing}"
        set_animation(self.animation, animation_name)
