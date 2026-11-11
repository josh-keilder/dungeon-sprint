import math

WALL_CHECK_RANGE = 64

STOP_SPEED = 1.0


def approach_fraction(rate, dt):
    return 1 - math.exp(-rate * dt)


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


def steer(
    velocity, direction, max_speed, acceleration_rate, deceleration_rate, grip, dt
):
    if direction.length_squared() > 0:
        target_velocity = direction * max_speed

        along_speed = velocity.dot(direction)
        along_velocity = direction * along_speed
        along_rate = grip if along_speed < 0 else acceleration_rate
        across_velocity = velocity - along_velocity
        new_along_velocity = along_velocity.lerp(
            target_velocity, approach_fraction(along_rate, dt)
        )
        new_across_velocity = across_velocity * (1 - approach_fraction(grip, dt))

        new_velocity = new_along_velocity + new_across_velocity
    else:
        new_velocity = decay_velocity(velocity, deceleration_rate, dt)

    return new_velocity


def decay_velocity(velocity, rate, dt):
    new_velocity = velocity * (1 - approach_fraction(rate, dt))

    if new_velocity.length_squared() < STOP_SPEED**2:
        new_velocity.update(0, 0)

    return new_velocity
