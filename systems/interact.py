from items.loot_table_data import CHEST_LOOT
from systems.inventory import add_item, has_item, remove_item
from systems.loot import roll_loot

REACH = 15


def find_target(player, level):
    reach_box = player.rect.inflate(REACH, REACH)

    for chest in level.chests:
        if reach_box.colliderect(chest.rect):
            return ("chest", chest)

    for item in level.ground_items:
        if reach_box.colliderect(item.rect):
            return ("item", item)

    if level.exit_rect is not None and reach_box.colliderect(level.exit_rect):
        return ("exit", level.exit_rect)

    for door in level.door_tiles:
        if reach_box.colliderect(door.rect):
            return ("door", door)

    return None


def describe_target(player, found):
    kind, target = found

    if kind == "chest":
        return ("Press F to open chest", True)
    if kind == "door":
        if has_item(player.inventory, "gold_key"):
            return ("Press F to unlock door", True)
        return ("Gold key required to unlock door", False)

    if kind == "exit":
        return ("Press F to climb down", True)

    return (f"Press F to pick up {target.item_data.name}", True)


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

    _, available = describe_target(player, found)
    if not available:
        return

    kind, target = found
    if kind == "chest":
        open_chest(target, level)
    elif kind == "door":
        unlock_door(level, target, player.inventory)
    elif kind == "item":
        pick_up_item(target, player.inventory)
    elif kind == "exit":
        level.exit_requested = True
