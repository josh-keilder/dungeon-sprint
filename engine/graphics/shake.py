import random

from engine.core.timer import advance_timer, is_running, new_timer, start_timer

# Screen shake: the camera jumps by up to `strength` world pixels, fading out
SHAKE_FADE = 20  # world pixels of strength lost per second
SHAKE_STEP = 1 / 30  # seconds between jumps, so it looks the same at any frame rate


def new_shake():
    return {"strength": 0.0, "offset": (0, 0), "step_timer": new_timer()}


def start_shake(shake, strength):
    # A weaker shake never cuts a strong one short
    shake["strength"] = max(shake["strength"], strength)


def update_shake(shake, dt):
    shake["strength"] = max(0.0, shake["strength"] - SHAKE_FADE * dt)

    advance_timer(shake["step_timer"], dt)
    if is_running(shake["step_timer"]):
        return

    start_timer(shake["step_timer"], SHAKE_STEP)
    reach = round(shake["strength"])
    shake["offset"] = (random.randint(-reach, reach), random.randint(-reach, reach))
