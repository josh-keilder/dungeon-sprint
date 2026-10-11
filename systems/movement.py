WALL_CHECK_RANGE = 64

TURN_BRAKE_THRESHOLD = -0.5
TURN_BRAKE_FACTOR = 0.01
IDLE_DRAG_MULTIPLIER = 1.2


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


def steer(velocity, direction, acceleration, friction, max_speed, dt):
    new_velocity = velocity.copy()

    if direction.length_squared() > 0:
        if (
            new_velocity.length_squared() > 0
            and direction.dot(new_velocity.normalize()) < TURN_BRAKE_THRESHOLD
        ):
            new_velocity -= new_velocity * friction * TURN_BRAKE_FACTOR * dt

        new_velocity += direction * acceleration * dt

    else:
        if new_velocity.length_squared() > 0:
            drop = new_velocity.normalize() * friction * IDLE_DRAG_MULTIPLIER * dt

            if new_velocity.length_squared() < drop.length_squared():
                new_velocity.update(0, 0)
            else:
                new_velocity -= drop

    if new_velocity.length_squared() > max_speed**2:
        new_velocity.scale_to_length(max_speed)

    return new_velocity
