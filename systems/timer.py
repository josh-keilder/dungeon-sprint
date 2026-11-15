def new_timer():
    return {"time_left": 0.0}


def start_timer(timer, duration):
    timer["time_left"] = duration


def advance_timer(timer, dt):
    timer["time_left"] -= dt


def is_running(timer):
    return timer["time_left"] > 0


def time_left(timer):
    return max(0.0, timer["time_left"])
