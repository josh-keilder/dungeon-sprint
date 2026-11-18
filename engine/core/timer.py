def new_timer():
    return {"time_left": 0.0, "duration": 0.0}


def start_timer(timer, duration):
    timer["time_left"] = duration
    timer["duration"] = duration


def advance_timer(timer, dt):
    timer["time_left"] -= dt


def is_running(timer):
    return timer["time_left"] > 0


def time_left(timer):
    return max(0.0, timer["time_left"])


def time_elapsed(timer):
    return timer["duration"] - time_left(timer)


def fraction_left(timer):
    # 1.0 just started, 0.0 finished (or never started)
    if timer["duration"] <= 0:
        return 0.0
    return time_left(timer) / timer["duration"]
