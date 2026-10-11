import pygame
import random

SIGHT_SEARCH_MARGIN = 64

FLEE_TIME = 2.0
RETURN_TIME = 3.0
CHASE_RANGE = 200
IDLE_TURN_CHANCE = 0.01
FLY_WANDER_FACTOR = 0.2
WALK_WANDER_FACTOR = 0.5


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


def random_idle_direction():
    return pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))


def trigger_flee(enemy):
    enemy.flee_timer = FLEE_TIME
    enemy.return_timer = RETURN_TIME


def fly_velocity(enemy, target_pos, dt):
    distance = enemy.pos.distance_to(target_pos)

    if enemy.flee_timer > 0:
        enemy.flee_timer -= dt
        dir_vector = (enemy.pos - target_pos).normalize() * enemy.speed
    elif enemy.return_timer > 0:
        enemy.return_timer -= dt
        dir_vector = (target_pos - enemy.pos).normalize() * enemy.speed
    elif distance < CHASE_RANGE:
        dir_vector = (target_pos - enemy.pos).normalize() * enemy.speed
    else:
        if random.random() < IDLE_TURN_CHANCE:
            enemy.idle_direction = random_idle_direction()
        dir_vector = enemy.idle_direction * enemy.speed * FLY_WANDER_FACTOR

    return dir_vector


def wander_chase_velocity(enemy, target_pos, walls):
    if has_line_of_sight(enemy.pos, target_pos, walls):
        dir_vector = (target_pos - enemy.pos).normalize() * enemy.speed
    else:
        if random.random() < IDLE_TURN_CHANCE:
            enemy.idle_direction = random_idle_direction()
        dir_vector = enemy.idle_direction * enemy.speed * WALK_WANDER_FACTOR

    return dir_vector
