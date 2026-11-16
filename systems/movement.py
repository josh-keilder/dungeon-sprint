import math

# Stopping: below this speed, a slowing body snaps to a stop
STOP_SPEED = 1.0  # pixels per second


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


def move_and_collide(rect, displacement, walls):
    # walls: a list of rects; collidelist returns the first one hit, or -1
    hit_x = False
    hit_y = False

    rect.x += displacement.x
    index = rect.collidelist(walls)
    if index != -1:
        wall = walls[index]
        if displacement.x > 0:
            rect.right = wall.left
        if displacement.x < 0:
            rect.left = wall.right
        hit_x = True

    rect.y += displacement.y
    index = rect.collidelist(walls)
    if index != -1:
        wall = walls[index]
        if displacement.y > 0:
            rect.bottom = wall.top
        if displacement.y < 0:
            rect.top = wall.bottom
        hit_y = True

    return hit_x, hit_y


def approach_fraction(rate, dt):
    return 1 - math.exp(-rate * dt)
