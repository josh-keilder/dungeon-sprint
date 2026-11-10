from systems.enemy_ai import trigger_flee
from systems.health import take_damage
from systems.timer import is_running, start_timer

ENEMY_CONTACT_DAMAGE = 20

INVULNERABILITY_DURATION = 1.0


def resolve_contact(player, enemy):
    if not is_running(player.invulnerability) and not player.roll["active"]:
        take_damage(player.health, enemy.attack_damage)
        start_timer(player.invulnerability, INVULNERABILITY_DURATION)

    if not is_running(enemy.invulnerability):
        take_damage(enemy.health, ENEMY_CONTACT_DAMAGE)
        start_timer(enemy.invulnerability, INVULNERABILITY_DURATION)

    trigger_flee(enemy)
