import random

import pygame

from systems.timer import advance_timer, is_running, start_timer

# Line of sight: only walls near the sight line are checked
SIGHT_SEARCH_MARGIN = 64  # pixels

# After a contact: run away, then come back
FLEE_TIME = 2.0  # seconds
RETURN_TIME = 3.0  # seconds

# Chasing
CHASE_RANGE = 200  # pixels; flyers chase the player inside this distance

# Wandering when not chasing
IDLE_TURN_CHANCE = 0.01  # chance per frame to pick a new direction
FLY_WANDER_FACTOR = 0.2  # fraction of full speed
WALK_WANDER_FACTOR = 0.5  # fraction of full speed


def random_idle_direction():
    return pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))


def trigger_flee(enemy):
    start_timer(enemy.flee_timer, FLEE_TIME)
    start_timer(enemy.return_timer, RETURN_TIME)


def fly_velocity(enemy, target_pos, dt):
    distance = enemy.pos.distance_to(target_pos)

    if is_running(enemy.flee_timer):
        advance_timer(enemy.flee_timer, dt)
        velocity = (enemy.pos - target_pos).normalize() * enemy.speed
    elif is_running(enemy.return_timer):
        advance_timer(enemy.return_timer, dt)
        velocity = (target_pos - enemy.pos).normalize() * enemy.speed
    elif distance < CHASE_RANGE:
        velocity = (target_pos - enemy.pos).normalize() * enemy.speed
    else:
        if random.random() < IDLE_TURN_CHANCE:
            enemy.idle_direction = random_idle_direction()
        velocity = enemy.idle_direction * enemy.speed * FLY_WANDER_FACTOR

    return velocity


def wander_chase_velocity(enemy, target_pos, walls):
    if has_line_of_sight(enemy.pos, target_pos, walls):
        velocity = (target_pos - enemy.pos).normalize() * enemy.speed
    else:
        if random.random() < IDLE_TURN_CHANCE:
            enemy.idle_direction = random_idle_direction()
        velocity = enemy.idle_direction * enemy.speed * WALK_WANDER_FACTOR

    return velocity


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
