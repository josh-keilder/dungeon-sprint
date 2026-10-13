from systems.enemy_ai import trigger_flee
from systems.health import take_damage

ENEMY_CONTACT_DAMAGE = 1


def resolve_contact(player, enemy):
    take_damage(player.health, enemy.attack_damage)
    take_damage(enemy.health, ENEMY_CONTACT_DAMAGE)
    trigger_flee(enemy)
