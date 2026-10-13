def new_health(max_health):
    return {"current": max_health, "max_health": max_health}


def take_damage(health, amount):
    health["current"] = max(0, health["current"] - amount)


def heal(health, amount):
    health["current"] = min(health["max_health"], health["current"] + amount)


def is_dead(health):
    return health["current"] <= 0


def set_max_health(health, new_max):
    health["max_health"] = new_max
    health["current"] = min(health["current"], new_max)
