DEFAULT_ANIMATION_SPEED = 10.0


def new_animation(frames, start_name, speed=DEFAULT_ANIMATION_SPEED):
    return {
        "frames": frames,
        "current": start_name,
        "index": 0,
        "timer": 0.0,
        "speed": speed,
    }


def set_animation(animation, name):
    if name != animation["current"]:
        if name in animation["frames"]:
            animation["current"] = name
            animation["index"] = 0
            animation["timer"] = 0.0


def advance_animation(animation, dt):
    animation["timer"] += animation["speed"] * dt

    while animation["timer"] >= 1:
        animation["timer"] -= 1
        animation["index"] += 1

    frames = animation["frames"][animation["current"]]

    animation["index"] %= len(frames)

    return frames[animation["index"]]
