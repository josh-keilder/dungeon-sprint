from globals import SMALL_HEALTH_POTION_VALUE
from systems.inventory import remove_item, has_item


def use_small_health_potion(health, inventory):
    at_full_health = health.current >= health.max_health
    has_small_health_potion = has_item(inventory, "small_health_potion")

    if at_full_health or not has_small_health_potion:
        return False

    health.heal(SMALL_HEALTH_POTION_VALUE)
    remove_item(inventory, "small_health_potion")

    return True
