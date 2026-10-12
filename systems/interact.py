from systems.inventory import has_item, remove_item, add_item

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

    for item in level.items:
        if reach_box.colliderect(item.rect):
            return ("item", item)

    return None


def open_chest(chest):
    chest.open()
    chest.kill()


def unlock_door(level, door, inventory):
    level.unlock_door(door.door_id)
    remove_item(inventory, "gold_key")


def pick_up_item(item, inventory):
    leftover = add_item(inventory, item.item_data.clone())
    if leftover == 0:
        item.kill
        return True

    item.item_data.quantity = leftover
    return False


def interact(player, level):
    found = find_target(player, level)

    if found is None:
        return

    kind, target = found
    if kind == "chest":
        open_chest(target)
    elif kind == "door":
        unlock_door(level, target, player.inventory)
    elif kind == "item":
        pick_up_item(target, player.inventory)
