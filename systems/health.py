def new_health(max_health):
    return {"current": max_health, "maximum": max_health}


def take_damage(health, amount):
    health["current"] = max(0, health["current"] - amount)


def heal(health, amount):
    health["current"] = min(health["maximum"], health["current"] + amount)


def is_dead(health):
    return health["current"] <= 0


def set_max_health(health, new_max):
    health["maximum"] = new_max
    health["current"] = min(health["current"], new_max)
