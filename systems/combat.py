from systems.enemy_ai import trigger_flee
from systems.health import take_damage
from systems.roll import is_rolling
from systems.timer import is_running, start_timer

INVULNERABILITY_DURATION = 1.0

# Damage per pixel per second of roll speed
ROLL_DAMAGE_PER_SPEED = 0.15


def resolve_contact(player, enemy):
    enemy_hit = False

    if is_rolling(player.roll) and not is_running(enemy.invulnerability):
        roll_damage = round(player.speed * ROLL_DAMAGE_PER_SPEED)
        take_damage(enemy.health, roll_damage)
        start_timer(enemy.invulnerability, INVULNERABILITY_DURATION)
        enemy_hit = True

    if not is_running(player.invulnerability) and not is_rolling(player.roll):
        take_damage(player.health, enemy.attack_damage)
        start_timer(player.invulnerability, INVULNERABILITY_DURATION)

    trigger_flee(enemy)
    return enemy_hit
