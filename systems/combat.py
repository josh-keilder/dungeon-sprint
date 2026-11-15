import pygame

from systems.enemy_ai import trigger_flee
from systems.health import take_damage
from systems.roll import is_rolling
from systems.timer import is_running, start_timer

# Player i-frames after being hit
PLAYER_INVULNERABILITY_DURATION = 1.0  # seconds

# Roll hits: both scale with the player's speed at the moment of impact
ROLL_DAMAGE_PER_SPEED = 0.15  # damage per pixel per second
KNOCKBACK_PER_SPEED = 1.2  # knockback speed per pixel per second


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
        enemy_hit = True

    if not is_running(player.invulnerability) and not is_rolling(player.roll):
        take_damage(player.health, enemy.attack_damage)
        start_timer(player.invulnerability, PLAYER_INVULNERABILITY_DURATION)

    trigger_flee(enemy)
    return enemy_hit
