def new_timer():
    return {"timer": 0.0}


def start_timer(timer, duration):
    timer["timer"] = duration


def advance_timer(timer, dt):
    timer["timer"] -= dt


def is_running(timer):
    return timer["timer"] > 0


def time_left(timer):
    return max(0.0, timer["timer"])
