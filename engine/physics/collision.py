import pygame

# Line of sight: only walls near the sight line are checked
SIGHT_SEARCH_MARGIN = 64  # pixels


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


def has_line_of_sight(start, end, walls):
    search_rect = pygame.Rect(
        min(start.x, end.x),
        min(start.y, end.y),
        abs(start.x - end.x),
        abs(start.y - end.y),
    ).inflate(SIGHT_SEARCH_MARGIN, SIGHT_SEARCH_MARGIN)

    for wall in walls:
        if not search_rect.colliderect(wall):
            continue
        if wall.clipline(start, end):
            return False
    return True


def edge_walls(wall_tiles, tile_size):
    # Walls next to open space (including diagonally); the rest can never be touched
    cells = {
        (wall.rect.x // tile_size, wall.rect.y // tile_size) for wall in wall_tiles
    }
    return [
        wall
        for wall in wall_tiles
        if any(
            (wall.rect.x // tile_size + dx, wall.rect.y // tile_size + dy) not in cells
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
        )
    ]
