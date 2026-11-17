import pygame

from constants import RED, TILE_SIZE, YELLOW
from engine.core import debug
from engine.core.assets import load_animations
from engine.core.timer import (
    advance_timer,
    is_running,
    new_timer,
    start_timer,
    time_left,
)
from engine.gameplay.health import new_health
from engine.graphics.animation import (
    DEFAULT_ANIMATION_SPEED,
    advance_animation,
    new_animation,
    set_animation,
)
from engine.graphics.blink import is_blink_hidden
from engine.graphics.masks import draw_hitbox
from engine.physics.movement import decay_velocity, move_and_collide
from systems.enemy_ai import fly_velocity, random_idle_direction, wander_chase_velocity
from ui_components.health_bar import draw_health_bar

# Health bar, in world pixels, shown above the sprite once the enemy is hurt
ENEMY_HEALTH_BAR_WIDTH = TILE_SIZE
ENEMY_HEALTH_BAR_HEIGHT = 2
ENEMY_HEALTH_BAR_GAP = 8  # from the sprite's top

# Animation states
HURT_DURATION = 0.5  # seconds of the hurt animation at the start of the i-frames


class Enemy:
    def __init__(self, type_data, pos):
        animations = load_animations(type_data["texture_data"])
        start_animation = type_data["start_animation"]

        # Values from the enemy type (ENEMY_TYPES)
        self.attack = type_data["attack"]
        self.attack_damage = type_data["attack_damage"]
        self.speed = type_data["speed"]
        self.knockback_multiplier = type_data["knockback_multiplier"]
        self.knockback_decay_rate = type_data["knockback_decay_rate"]
        self.blink_interval = type_data["blink_interval"]
        self.invulnerability_duration = type_data["invulnerability_duration"]
        self.loot_table = type_data["loot_table"]
        self.behavior = type_data["behavior"]
        self.touch_damage = type_data["touch_damage"]
        self.animation_prefix = type_data["animation_prefix"]
        self.hit_particles = type_data["hit_particles"]
        self.stagger_duration = type_data["stagger_duration"]

        # Position, sprite and animation
        self.pos = pygame.math.Vector2(pos)
        self.animation = new_animation(animations, start_animation)
        self.image = animations[start_animation][0]

        # Animation state: which way it faces, whether it moved, and dying
        self.facing = "right"
        self.moving = False
        self.dying = False
        self.death_time = 0.0
        death_frames = animations.get(f"{self.animation_prefix}_death_right", [])
        self.death_duration = len(death_frames) / DEFAULT_ANIMATION_SPEED

        # Body: the box that moves, hits walls and gets hit; the art is drawn around it
        body_x, body_y, body_width, body_height = type_data["body"]
        self.body_x = body_x
        self.body_y = body_y
        self.rect = pygame.FRect(self.pos, (body_width, body_height))

        # Health and hit timers
        self.health = new_health(type_data["max_health"])
        self.invulnerability = new_timer()
        self.stagger = new_timer()

        # AI state
        self.flee_timer = new_timer()
        self.return_timer = new_timer()
        self.idle_direction = random_idle_direction()

        # Swing state (only for types with an "attack")
        self.attacking = False
        self.attack_time = 0.0
        self.attack_landed = False
        self.attack_cooldown = new_timer()

        # Knockback from roll hits, decayed each frame
        self.knockback_velocity = pygame.Vector2()

    def update(self, dt, walls, target_pos):
        if self.dying:
            self.death_time += dt
            self.update_knockback(dt, walls)
        else:
            start_center = pygame.Vector2(self.rect.center)
            if self.attacking:
                velocity = pygame.Vector2()
                self.update_attack(dt)
            elif self.is_staggered():
                velocity = pygame.Vector2()
            else:
                velocity = self.update_movement(dt, walls, target_pos)
                self.try_start_attack(target_pos)

            self.update_knockback(dt, walls)
            advance_timer(self.invulnerability, dt)
            advance_timer(self.stagger, dt)
            advance_timer(self.attack_cooldown, dt)

            self.moving = pygame.Vector2(self.rect.center) != start_center
            if velocity.x < 0:
                self.facing = "left"
            elif velocity.x > 0:
                self.facing = "right"

        self.update_animation(dt)
        self.pos.xy = self.rect.topleft

    def draw(self, screen, camera=None):
        blink_hidden = (
            not self.dying
            and self.blink_interval is not None
            and is_blink_hidden(self.invulnerability, self.blink_interval)
        )

        art_x, art_y = self.art_topleft()
        draw_pos = (art_x, art_y)
        if camera:
            draw_pos = (art_x - camera.x, art_y - camera.y)

        if not blink_hidden:
            screen.blit(self.image, draw_pos)

        if self.health["current"] < self.health["maximum"] and not self.dying:
            bar_x = self.rect.centerx - ENEMY_HEALTH_BAR_WIDTH // 2
            bar_y = self.rect.top - ENEMY_HEALTH_BAR_GAP

            bar_pos = (bar_x, bar_y)
            if camera:
                bar_pos = (bar_x - camera.x, bar_y - camera.y)

            draw_health_bar(
                screen,
                self.health,
                *bar_pos,
                ENEMY_HEALTH_BAR_WIDTH,
                ENEMY_HEALTH_BAR_HEIGHT,
            )

        if debug.show_hitboxes:
            art_rect = pygame.FRect(self.art_topleft(), self.image.get_size())
            draw_hitbox(screen, self.image, art_rect, camera, RED)
            body_on_screen = (
                self.rect.move(-camera.x, -camera.y) if camera else self.rect
            )

            if self.is_striking():
                strike_on_screen = (
                    self.strike_rect().move(-camera.x, -camera.y)
                    if camera
                    else self.strike_rect()
                )
                pygame.draw.rect(screen, RED, strike_on_screen, 1)

            pygame.draw.rect(screen, YELLOW, body_on_screen, 1)

    def art_topleft(self):
        offset_x = self.body_x
        if self.facing == "left":
            offset_x = self.image.get_width() - self.body_x - self.rect.width
        return (self.rect.x - offset_x, self.rect.y - self.body_y)

    def update_animation(self, dt):
        if self.attacking:
            self.image = self.attack_frames()[self.attack_step()]
            return

        if self.animation_prefix is not None:
            set_animation(self.animation, self.animation_name())
        self.image = advance_animation(self.animation, dt)

    def animation_name(self):
        if self.dying:
            action = "death"
        elif (
            time_left(self.invulnerability)
            > self.invulnerability_duration - HURT_DURATION
        ):
            action = "hurt"
        elif self.moving:
            action = "move"
        else:
            action = "idle"
        return f"{self.animation_prefix}_{action}_{self.facing}"

    def update_movement(self, dt, walls, target_pos):
        if self.behavior == "fly":
            velocity = fly_velocity(self, target_pos, dt)
            self.rect.x += velocity.x * dt
            self.rect.y += velocity.y * dt
            return velocity

        elif self.behavior == "wander_chase":
            chase_pos = target_pos
            if self.attack is not None:
                chase_pos = self.line_up_spot(target_pos)
            velocity = wander_chase_velocity(self, target_pos, walls, chase_pos)
            move_and_collide(self.rect, velocity * dt, walls)
            return velocity

    def update_knockback(self, dt, walls):
        hit_x, hit_y = move_and_collide(self.rect, self.knockback_velocity * dt, walls)

        if hit_x:
            self.knockback_velocity.x = 0
        if hit_y:
            self.knockback_velocity.y = 0

        self.knockback_velocity = decay_velocity(
            self.knockback_velocity, self.knockback_decay_rate, dt
        )

    def is_staggered(self):
        # After a roll hit: no walking or new swings while being pushed, or for
        # the type's stagger time, whichever is longer
        return is_running(self.stagger) or self.knockback_velocity.length_squared() > 0

    def shove(self, displacement, walls):
        move_and_collide(self.rect, displacement, walls)
        self.pos.xy = self.rect.topleft

    def try_start_attack(self, target_pos):
        if self.attack is None or is_running(self.attack_cooldown):
            return
        if self.pos.distance_to(target_pos) > self.attack["range"]:
            return
        if abs(target_pos.y - self.pos.y) > self.attack["level_tolerance"]:
            return

        self.attacking = True
        self.attack_time = 0.0
        self.attack_landed = False
        self.facing = "right" if target_pos.x >= self.pos.x else "left"

    def line_up_spot(self, target_pos):
        # The swing only reaches sideways, so walk beside the target, level with it
        side = 1 if self.pos.x >= target_pos.x else -1
        return pygame.Vector2(
            target_pos.x + side * self.attack["line_up_gap"], target_pos.y
        )

    def update_attack(self, dt):
        self.attack_time += dt
        if self.attack_step() >= len(self.attack_frames()):
            self.attacking = False
            start_timer(self.attack_cooldown, self.attack["cooldown"])

    def attack_frames(self):
        return self.animation["frames"][f"{self.animation_prefix}_attack_{self.facing}"]

    def attack_step(self):
        return int(self.attack_time * self.attack["frame_rate"])

    def is_striking(self):
        return self.attacking and self.attack_step() in self.attack["strike_frames"]

    def strike_rect(self):
        reach = self.attack["reach"]
        strike = pygame.FRect(0, self.rect.y, reach, self.rect.height)
        if self.facing == "right":
            strike.left = self.rect.right
        else:
            strike.right = self.rect.left
        return strike

    def interrupt_attack(self):
        if self.attacking and not self.is_striking() and not self.attack_landed:
            self.attacking = False
            start_timer(self.attack_cooldown, self.attack["cooldown"])

    def start_dying(self):
        self.dying = True
        self.death_time = 0.0
        self.attacking = False

    def is_done_dying(self):
        return self.dying and self.death_time >= self.death_duration

    def is_solid(self):
        return not self.dying and self.behavior != "fly"
