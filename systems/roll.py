ROLL_DURATION = 0.4
ROLL_COOLDOWN = 1.0


def try_start_roll(roll, direction):
    if direction.length_squared() == 0:
        return False

    if not roll["active"] and roll["cooldown"] <= 0:
        roll["active"] = True
        roll["timer"] = ROLL_DURATION
        roll["cooldown"] = ROLL_COOLDOWN
        roll["direction"] = direction.copy()

        return True
    return False


def advance_roll(roll, dt):
    if roll["active"]:
        roll["timer"] -= dt
        if roll["timer"] <= 0:
            roll["active"] = False

    roll["cooldown"] -= dt
