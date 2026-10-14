import pygame

from globals import GREEN
from systems import debug
from systems.animation import advance_animation, new_animation, set_animation
from systems.consumables import use_small_health_potion
from systems.health import new_health, set_max_health
from systems.hitbox import draw_hitbox
from systems.inventory import new_inventory
from systems.movement import move_and_collide, steer
from systems.roll import advance_roll, try_start_roll
from systems.stats import compute_stats


class Player:
    def __init__(self, animations, pos=(0, 0)):

        self.last_direction = "down"
        self.walking = False
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.Vector2()

        self.intent = {"move": pygame.Vector2(), "roll": False, "heal": False}

        # Base values before equipment bonuses
        self.base_stats = {
            "attack": 5,
            "defense": 0,
            "max_speed": 70,
            "health": 500,
            "roll_speed": 200,
            "acceleration": 47,
            "friction": 3000,
        }

        self.roll = {
            "active": False,
            "direction": pygame.Vector2(),
            "timer": 0.0,
            "cooldown": 0.0,
        }

        # Animation and sprite
        self.animation = new_animation(animations, "player_idle_down")
        self.image = animations["player_idle_down"][0]
        self.rect = self.image.get_frect()
        self.rect.center = pos

        # Health, inventory, and stats
        self.health = new_health(self.base_stats["health"])

        self.inventory = new_inventory(20)

        self.stats = compute_stats(
            self.base_stats, self.inventory["equipment"].values()
        )

    def update(self, dt, walls):

        move_direction = self.intent["move"]
        self.walking = move_direction.length_squared() > 0
        if self.walking and not self.roll["active"]:
            self.update_facing(move_direction)

        self.stats = compute_stats(
            self.base_stats, self.inventory["equipment"].values()
        )

        if self.health["max_health"] != self.stats["health"]:
            set_max_health(self.health, self.stats["health"])

        # Actions requested this frame
        if self.intent["roll"]:
            try_start_roll(self.roll, move_direction)

        if self.intent["heal"]:
            use_small_health_potion(self.health, self.inventory)

        self.update_movement(dt, walls)
        self.update_roll(dt, walls)

        self.handle_animation_state()
        self.image = advance_animation(self.animation, dt)

        self.pos = pygame.math.Vector2(self.rect.topleft)

    def draw(self, screen, camera=None):
        if camera:
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
        else:
            screen.blit(self.image, self.rect.topleft)

        if debug.show_hitboxes:
            draw_hitbox(screen, self.image, self.rect, camera, GREEN)

    def handle_animation_state(self):
        if self.roll["active"]:
            action = "roll"
        elif self.walking:
            action = "walk"
        else:
            action = "idle"

        animation_name = f"player_{action}_{self.last_direction}"
        set_animation(self.animation, animation_name)

    def update_facing(self, move_direction):
        if move_direction.y < 0:
            self.last_direction = "up"
        elif move_direction.y > 0:
            self.last_direction = "down"
        elif move_direction.x < 0:
            self.last_direction = "left"
        elif move_direction.x > 0:
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
