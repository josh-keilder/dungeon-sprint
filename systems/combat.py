from systems.enemy_ai import trigger_flee

ENEMY_CONTACT_DAMAGE = 1


def resolve_contact(player, enemy):
    player.health.take_damage(enemy.attack_damage)
    enemy.health.take_damage(ENEMY_CONTACT_DAMAGE)
    trigger_flee(enemy)
