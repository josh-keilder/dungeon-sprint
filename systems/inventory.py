EQUIPMENT_SLOT_NAMES = ("head", "chest", "boots", "ability_1", "ability_2")


def new_inventory(slot_count):
    return {
        "slots": [None] * slot_count,
        "equipment": {name: None for name in EQUIPMENT_SLOT_NAMES},
    }


def add_item(inventory, item):
    for slot in inventory["slots"]:
        if slot and slot.id == item.id:
            space_available = slot.max_stack - slot.quantity
            if space_available > 0:
                amount_to_add = min(space_available, item.quantity)
                slot.quantity += amount_to_add
                item.quantity -= amount_to_add

                if item.quantity <= 0:
                    return 0

    if item.quantity > 0:
        for slot_index in range(len(inventory["slots"])):
            if inventory["slots"][slot_index] is None:
                inventory["slots"][slot_index] = item.clone()
                return 0

    return item.quantity


def remove_item(inventory, item_id, quantity=1):
    total_found = count_item(inventory, item_id)

    if total_found < quantity:
        return False

    remaining_to_remove = quantity
    for slot_index in range(len(inventory["slots"])):
        slot = inventory["slots"][slot_index]

        if slot and slot.id == item_id:
            if slot.quantity > remaining_to_remove:
                slot.quantity -= remaining_to_remove
                remaining_to_remove = 0
                break
            else:
                remaining_to_remove -= slot.quantity
                inventory["slots"][slot_index] = None

            if remaining_to_remove <= 0:
                break

    return True


def has_item(inventory, item_id, quantity=1):
    return count_item(inventory, item_id) >= quantity


def count_item(inventory, item_id):
    return sum(
        slot.quantity for slot in inventory["slots"] if slot and slot.id == item_id
    )


def can_equip(item, slot_name):
    return getattr(item, "slot", None) == slot_name
