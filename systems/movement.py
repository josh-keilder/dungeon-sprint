WALL_CHECK_RANGE = 64


def move_and_collide(rect, displacement, walls):
    hit_x = False
    hit_y = False

    rect.x += displacement.x
    for wall in walls:
        if abs(rect.centerx - wall.rect.centerx) > WALL_CHECK_RANGE:
            continue
        if rect.colliderect(wall.rect):
            if displacement.x > 0:
                rect.right = wall.rect.left
            if displacement.x < 0:
                rect.left = wall.rect.right
            hit_x = True
            break

    rect.y += displacement.y
    for wall in walls:
        if abs(rect.centery - wall.rect.centery) > WALL_CHECK_RANGE:
            continue
        if rect.colliderect(wall.rect):
            if displacement.y > 0:
                rect.bottom = wall.rect.top
            if displacement.y < 0:
                rect.top = wall.rect.bottom
            hit_y = True
            break

    return hit_x, hit_y
