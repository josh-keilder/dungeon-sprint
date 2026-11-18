from engine.physics.collision import push_out
from systems.roll import is_rolling

# Solid enemies (walkers, not fliers) may not stack on each other or sit on the player:
# overlapping bodies are pushed apart along the shortest way out, after combat has had its
# chance to see the overlap.


def separate_enemies(enemies, player, walls):
    solid_enemies = [enemy for enemy in enemies if enemy.is_solid()]

    for index, enemy in enumerate(solid_enemies):
        for other in solid_enemies[index + 1 :]:
            push = push_out(enemy.rect, other.rect)
            if push is not None:
                enemy.shove(push / 2, walls)
                other.shove(-push / 2, walls)

        if not is_rolling(player.roll):
            push = push_out(enemy.rect, player.rect)
            if push is not None:
                enemy.shove(push, walls)
