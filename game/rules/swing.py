import pygame

from engine.core.timer import is_running, new_timer, start_timer

# The sword swing of enemy types with an "attack" (the Skeleton): wind up, hurt on the
# strike frames, then wait out the cooldown. The state lives in enemy.swing, the numbers
# in enemy.attack (from ENEMY_TYPES).


def new_swing():
    return {
        "active": False,
        "time": 0.0,  # seconds since this swing started
        "landed": False,  # this swing already hit the player
        "cooldown": new_timer(),
    }


def line_up_spot(enemy, target_pos):
    # The swing only reaches sideways, so walk beside the target, level with it
    side = 1 if enemy.pos.x >= target_pos.x else -1
    return pygame.Vector2(
        target_pos.x + side * enemy.attack["line_up_gap"], target_pos.y
    )


def try_start_swing(enemy, target_pos):
    swing = enemy.swing
    if enemy.attack is None or is_running(swing["cooldown"]):
        return
    if enemy.pos.distance_to(target_pos) > enemy.attack["range"]:
        return
    if abs(target_pos.y - enemy.pos.y) > enemy.attack["level_tolerance"]:
        return

    swing["active"] = True
    swing["time"] = 0.0
    swing["landed"] = False
    enemy.facing = "right" if target_pos.x >= enemy.pos.x else "left"


def update_swing(enemy, dt):
    enemy.swing["time"] += dt
    if swing_step(enemy) >= len(swing_frames(enemy)):
        end_swing(enemy)


def end_swing(enemy):
    enemy.swing["active"] = False
    start_timer(enemy.swing["cooldown"], enemy.attack["cooldown"])


def interrupt_swing(enemy):
    # A roll hit cancels the wind-up, but never a strike that's already out
    swing = enemy.swing
    if swing["active"] and not is_striking(enemy) and not swing["landed"]:
        end_swing(enemy)


def swing_frames(enemy):
    return enemy.animation["frames"][f"{enemy.animation_prefix}_attack_{enemy.facing}"]


def swing_step(enemy):
    return int(enemy.swing["time"] * enemy.attack["frame_rate"])


def is_striking(enemy):
    return enemy.swing["active"] and swing_step(enemy) in enemy.attack["strike_frames"]


def strike_rect(enemy):
    reach = enemy.attack["reach"]
    strike = pygame.FRect(0, enemy.rect.y, reach, enemy.rect.height)
    if enemy.facing == "right":
        strike.left = enemy.rect.right
    else:
        strike.right = enemy.rect.left
    return strike
