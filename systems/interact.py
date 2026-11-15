from items.loot_table_data import CHEST_LOOT
from systems.inventory import add_item, has_item, remove_item
from systems.loot import roll_loot

# Reach: how far around the player F can act
REACH = 15  # pixels added to the player's rect (split over both sides)


def interact(player, floor):
    found = find_target(player, floor)

    if found is None:
        return

    _, available = describe_target(player, found)
    if not available:
        return

    kind, target = found
    if kind == "chest":
        open_chest(target, floor)
    elif kind == "door":
        unlock_door(floor, target, player.inventory)
    elif kind == "item":
        pick_up_item(target, player.inventory)
    elif kind == "exit":
        floor.exit_requested = True


def find_target(player, floor):
    reach_box = player.rect.inflate(REACH, REACH)

    for chest in floor.chests:
        if reach_box.colliderect(chest.rect):
            return ("chest", chest)

    for item in floor.ground_items:
        if reach_box.colliderect(item.rect):
            return ("item", item)

    if floor.exit_rect is not None and reach_box.colliderect(floor.exit_rect):
        return ("exit", floor.exit_rect)

    for door in floor.door_tiles:
        if reach_box.colliderect(door.rect):
            return ("door", door)

    return None


def describe_target(player, found):
    kind, target = found

    if kind == "chest":
        return ("Press F to open chest", True)
    if kind == "door":
        if has_item(player.inventory, target.key):
            return ("Press F to unlock door", True)

        key_name = target.key.replace("_", " ").capitalize()
        return (f"{key_name} required to unlock door", False)

    if kind == "exit":
        return ("Press F to climb down", True)

    return (f"Press F to pick up {target.item_data.name}", True)


def open_chest(chest, floor):
    drops = roll_loot(CHEST_LOOT)
    floor.spawn_loot(drops, chest.rect.center)
    chest.kill()


def unlock_door(floor, door, inventory):
    floor.unlock_door(door.door_id)
    remove_item(inventory, door.key)


def pick_up_item(item, inventory):
    leftover = add_item(inventory, item.item_data.clone())
    if leftover == 0:
        item.kill()
        return True

    item.item_data.quantity = leftover
    return False
