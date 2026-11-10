from globals import SMALL_HEALTH_POTION_VALUE
from systems.health import heal
from systems.inventory import has_item, remove_item

HEAL_COOLDOWN = 3.0


def use_small_health_potion(health, inventory, heal_cooldown):
    if heal_cooldown["timer"] > 0:
        return False

    at_full_health = health["current"] >= health["max_health"]
    has_small_health_potion = has_item(inventory, "small_health_potion")

    if at_full_health or not has_small_health_potion:
        return False

    heal(health, SMALL_HEALTH_POTION_VALUE)
    heal_cooldown["timer"] = HEAL_COOLDOWN
    remove_item(inventory, "small_health_potion")

    return True


def advance_heal_cooldown(heal_cooldown, dt):
    heal_cooldown["timer"] -= dt
