from systems.timer import advance_timer, is_running, start_timer, time_left

ROLL_DURATION = 0.4
ROLL_COOLDOWN = 1.0
ROLL_EASE_OUT_START = 0.7


def try_start_roll(roll, direction):
    if direction.length_squared() == 0:
        return False

    if not is_rolling(roll) and not is_running(roll["cooldown_timer"]):
        start_timer(roll["active_timer"], ROLL_DURATION)
        start_timer(roll["cooldown_timer"], ROLL_COOLDOWN)
        roll["direction"] = direction.copy()

        return True
    return False


def advance_roll(roll, dt):
    advance_timer(roll["cooldown_timer"], dt)
    advance_timer(roll["active_timer"], dt)


def is_rolling(roll):
    return is_running(roll["active_timer"])


def roll_speed_multiplier(roll):
    progress = 1 - time_left(roll["active_timer"]) / ROLL_DURATION

    if progress < ROLL_EASE_OUT_START:
        return 1.0
    else:
        return (1 - progress) / (1 - ROLL_EASE_OUT_START)
