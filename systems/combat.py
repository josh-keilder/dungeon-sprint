from systems.enemy_ai import trigger_flee
from systems.health import take_damage
from systems.invulnerability import is_invulnerable, start_invulnerability

ENEMY_CONTACT_DAMAGE = 20


def resolve_contact(player, enemy):

    if not is_invulnerable(player.invulnerability) and not player.roll["active"]:
        take_damage(player.health, enemy.attack_damage)
        start_invulnerability(player.invulnerability)

    if not is_invulnerable(enemy.invulnerability):
        take_damage(enemy.health, ENEMY_CONTACT_DAMAGE)
        start_invulnerability(enemy.invulnerability)

    trigger_flee(enemy)
