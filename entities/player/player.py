import pygame

from globals import GREEN
from systems import debug
from systems.animation import advance_animation, new_animation, set_animation
from systems.consumables import use_small_health_potion
from systems.health import new_health, set_max_health
from systems.hitbox import draw_hitbox
from systems.inventory import new_inventory
from systems.movement import move_and_collide, steer
from systems.roll import advance_roll, is_rolling, roll_speed_multiplier, try_start_roll
from systems.sound import play_sfx
from systems.stats import compute_stats
from systems.timer import advance_timer, is_running, new_timer, time_left

BLINK_INTERVAL = 0.1


class Player:
    def __init__(self, animations, pos=(0, 0)):
        self.last_direction = "down"
        self.walking = False
        self.pos = pygame.math.Vector2(pos)

        self.velocity = pygame.Vector2()
        self.speed = 0.0

        self.intent = {"move": pygame.Vector2(), "roll": False, "heal": False}

        # Base values before equipment bonuses
        self.base_stats = {
            "defense": 0,
            "health": 25,
            "roll_speed": 200,
            "max_speed": 70,
            "acceleration_rate": 20,
            "deceleration_rate": 60,
            "grip": 50,
        }

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
        self.rect.center = pos

        # Health, inventory, and stats
        self.health = new_health(self.base_stats["health"])

        self.inventory = new_inventory(20)

        self.stats = compute_stats(
            self.base_stats, self.inventory["equipment"].values()
        )

    def update(self, dt, walls):
        # Before anything moves the player, store where the player is.
        start_pos = pygame.Vector2(self.rect.center)

        move_direction = self.intent["move"]
        self.walking = move_direction.length_squared() > 0
        if self.walking and not is_rolling(self.roll):
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
            healed = use_small_health_potion(
                self.health, self.inventory, self.heal_cooldown
            )
            if healed:
                play_sfx("heal")

        self.update_movement(dt, walls)
        self.update_roll(dt, walls)

        # Distance moved calculation comes after the movement updates, then calculate the player speed during that distance
        distance_moved = pygame.Vector2(self.rect.center).distance_to(start_pos)
        self.speed = distance_moved / dt

        advance_timer(self.invulnerability, dt)
        advance_timer(self.heal_cooldown, dt)

        self.handle_animation_state()
        self.image = advance_animation(self.animation, dt)

        self.pos = pygame.math.Vector2(self.rect.topleft)

    def draw(self, screen, camera=None):
        blink_phase = int(time_left(self.invulnerability) / BLINK_INTERVAL)
        blink_hidden = is_running(self.invulnerability) and blink_phase % 2 == 1

        if not blink_hidden:
            if camera:
                screen.blit(
                    self.image, (self.rect.x - camera.x, self.rect.y - camera.y)
                )
            else:
                screen.blit(self.image, self.rect.topleft)

        if debug.show_hitboxes:
            draw_hitbox(screen, self.image, self.rect, camera, GREEN)

    def handle_animation_state(self):
        if is_rolling(self.roll):
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
