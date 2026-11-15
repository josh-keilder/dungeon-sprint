import pygame

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


def push_out(rect, other_rect):
    overlap = rect.clip(other_rect)
    if overlap.width == 0 or overlap.height == 0:
        return None

    away = pygame.Vector2(rect.center) - pygame.Vector2(other_rect.center)
    if overlap.width < overlap.height:
        direction = 1 if away.x >= 0 else -1
        return pygame.Vector2(overlap.width * direction, 0)

    direction = 1 if away.y >= 0 else -1
    return pygame.Vector2(0, overlap.height * direction)
