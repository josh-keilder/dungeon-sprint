REACH = 15


def find_target(player, level):
    reach_box = player.rect.inflate(REACH, REACH)

    for chest in level.chests:
        if reach_box.colliderect(chest.rect):
            return ("chest", chest)

    if player.inventory.has_item("gold_key"):
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
    inventory.remove_item("gold_key")


def pick_up_item(item, inventory):
    if inventory.add_item(item.item_data.clone()):
        item.kill()
        return True

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
