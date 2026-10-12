from Components.component import Component
from typing import List, Optional, Dict, Any, Tuple


class InventoryComponent(Component):
    def __init__(self, node: Any, size: int) -> None:
        self.node = node
        self.inventory_slots = [None] * size

        self.equipment_slots = {
            "head": None,
            "chest": None,
            "boots": None,
            "ability_1": None,
            "ability_2": None,
        }

    def add_item(self, item: Any) -> bool:
        """Adds an item to the inventory, prioritizing existing stacks of the same ID."""
        for slot in self.inventory_slots:
            if slot and slot.id == item.id:
                space_available = slot.max_stack - slot.quantity
                if space_available > 0:
                    amount_to_add = min(space_available, item.quantity)
                    slot.quantity += amount_to_add
                    item.quantity -= amount_to_add

                    if item.quantity <= 0:
                        return True

        if item.quantity > 0:
            for i in range(len(self.inventory_slots)):
                if self.inventory_slots[i] is None:
                    self.inventory_slots[i] = item.clone()
                    return True

        return False

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Removes a specific quantity of an item across all stacks in the inventory."""
        total_found = sum(
            slot.quantity
            for slot in self.inventory_slots
            if slot and slot.id == item_id
        )

        if total_found < quantity:
            return False

        remaining_to_remove = quantity
        for i in range(len(self.inventory_slots)):
            slot = self.inventory_slots[i]

            if slot and slot.id == item_id:
                if slot.quantity > remaining_to_remove:
                    slot.quantity -= remaining_to_remove
                    remaining_to_remove = 0
                    break
                else:
                    remaining_to_remove -= slot.quantity
                    self.inventory_slots[i] = None

                if remaining_to_remove <= 0:
                    break

        return True

    def get_item(self, item_id: str) -> Optional[Any]:
        """Searches for and returns the first instance of an item matching the ID."""
        for slot in self.inventory_slots:
            if slot and slot.id == item_id:
                return slot
        return None

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Checks if the inventory contains at least the specified quantity of an item."""
        item = self.get_item(item_id)
        return item is not None and item.quantity >= quantity
