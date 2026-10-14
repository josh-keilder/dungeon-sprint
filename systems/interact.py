from items.loot_table_data import CHEST_LOOT
from systems.inventory import add_item, has_item, remove_item
from systems.loot import roll_loot

REACH = 15


def find_target(player, level):
    reach_box = player.rect.inflate(REACH, REACH)

    for chest in level.chests:
        if reach_box.colliderect(chest.rect):
            return ("chest", chest)

    if has_item(player.inventory, "gold_key"):
        for door in level.door_tiles:
            if reach_box.colliderect(door.rect):
                return ("door", door)

    for item in level.ground_items:
        if reach_box.colliderect(item.rect):
            return ("item", item)

    return None


def open_chest(chest, level):
    drops = roll_loot(CHEST_LOOT)
    level.spawn_loot(drops, chest.rect.center)
    chest.kill()


def unlock_door(level, door, inventory):
    level.unlock_door(door.door_id)
    remove_item(inventory, "gold_key")


def pick_up_item(item, inventory):
    leftover = add_item(inventory, item.item_data.clone())
    if leftover == 0:
        item.kill()
        return True

    item.item_data.quantity = leftover
    return False


def interact(player, level):
    found = find_target(player, level)

    if found is None:
        return

    kind, target = found
    if kind == "chest":
        open_chest(target, level)
    elif kind == "door":
        unlock_door(level, target, player.inventory)
    elif kind == "item":
        pick_up_item(target, player.inventory)
