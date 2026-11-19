import pygame

from engine.core.timer import is_running, start_timer
from engine.gameplay.health import is_dead, take_damage
from engine.graphics.particles import emit_burst
from engine.io import sound
from game.rules.contacts import find_player_contacts
from game.rules.enemy_ai import trigger_flee
from game.rules.roll import is_rolling
from game.rules.swing import interrupt_swing, is_striking, strike_rect

# Player i-frames after being hit
PLAYER_INVULNERABILITY_DURATION = 1.0  # seconds

# Player knockback when hurt
PLAYER_KNOCKBACK_SPEED = 160  # pixels per second, away from the enemy

# Roll hits: both scale with the player's speed at the moment of impact
ROLL_DAMAGE_PER_SPEED = 0.15  # damage per pixel per second
KNOCKBACK_PER_SPEED = 1.2  # knockback speed per pixel per second


def resolve_combat(player, enemies, particles):
    # Roll hits and touches first, then sword strikes; returns whether a roll hit landed
    hit_landed = False

    living_enemies = [enemy for enemy in enemies if not enemy.dying]
    for enemy in find_player_contacts(player, living_enemies):
        if resolve_contact(player, enemy):
            sound.play_sfx("roll_hit")
            emit_burst(
                particles,
                enemy.rect.center,
                enemy.hit_particles,
                enemy.knockback_velocity,
            )
            hit_landed = True

        if is_dead(enemy.health):
            enemy.start_dying()

    # An enemy killed just now can't strike back
    for enemy in enemies:
        if enemy.attack is not None and not enemy.dying:
            resolve_strike(player, enemy)

    return hit_landed


def resolve_contact(player, enemy):
    enemy_hit = False

    if is_rolling(player.roll) and not is_running(enemy.invulnerability):
        roll_damage = round(player.speed * ROLL_DAMAGE_PER_SPEED)
        take_damage(enemy.health, roll_damage)
        knockback_direction = pygame.Vector2(enemy.rect.center) - pygame.Vector2(
            player.rect.center
        )
        if knockback_direction.length_squared() > 0:
            knockback_direction.normalize_ip()
        else:
            knockback_direction = player.roll["direction"].copy()

        enemy.knockback_velocity = (
            knockback_direction
            * player.speed
            * KNOCKBACK_PER_SPEED
            * enemy.knockback_multiplier
        )

        start_timer(enemy.invulnerability, enemy.invulnerability_duration)
        start_timer(enemy.stagger, enemy.stagger_duration)

        if enemy.attack is not None:
            interrupt_swing(enemy)

        enemy_hit = True

    if (
        enemy.touch_damage
        and not is_running(player.invulnerability)
        and not is_rolling(player.roll)
    ):
        hurt_player(player, enemy)

    trigger_flee(enemy)
    return enemy_hit


def resolve_strike(player, enemy):
    if enemy.swing["landed"] or not is_striking(enemy):
        return False
    if not player.rect.colliderect(strike_rect(enemy)):
        return False

    enemy.swing["landed"] = True
    if is_running(player.invulnerability) or is_rolling(player.roll):
        return False

    hurt_player(player, enemy)
    return True


def hurt_player(player, enemy):
    take_damage(player.health, enemy.attack_damage)
    start_timer(player.invulnerability, PLAYER_INVULNERABILITY_DURATION)

    push_direction = pygame.Vector2(player.rect.center) - pygame.Vector2(
        enemy.rect.center
    )
    if push_direction.length_squared() > 0:
        player.knockback_velocity = push_direction.normalize() * PLAYER_KNOCKBACK_SPEED
