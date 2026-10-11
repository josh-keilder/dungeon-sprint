import pygame

SIGHT_SEARCH_MARGIN = 64


def has_line_of_sight(start, end, walls):
    search_rect = pygame.Rect(
        min(start.x, end.x),
        min(start.y, end.y),
        abs(start.x - end.x),
        abs(start.y - end.y),
    ).inflate(SIGHT_SEARCH_MARGIN, SIGHT_SEARCH_MARGIN)

    for wall in walls:
        if not search_rect.colliderect(wall.rect):
            continue
        if wall.rect.clipline(start, end):
            return False
    return True
