"""
System: Inventory and Equipment Management
------------------------------------------
Handles the storage, retrieval, and UI rendering of items within a grid-based
inventory and specific equipment slots. Manages drag-and-drop interactions,
stackable item logic, and dynamic tooltip generation.

Classes:
    InventoryComponent: Manages item stacks, equipment, and UI interaction logic.
"""

import pygame
from globals import *
from Components.component import Component
from ui_objects.text_loader import Text_Loader
from items.items import EquipmentItem
from typing import List, Optional, Dict, Any, Tuple


class InventoryComponent(Component):
    def __init__(self, node: Any, size: int, cols: int = 10) -> None:
        """Initializes inventory grids, equipment slots, and UI text elements."""
        self.node = node
        self.size = size
        self.cols = cols
        self.inventory_slots = [None] * size
        self.slot_size = 48
        self.padding = 2

        self.equipment_slots = {
            "head": None,
            "chest": None,
            "boots": None,
            "ability_1": None,
            "ability_2": None,
        }

        # UI Text Loaders for item quantities and metadata
        self.quantity_label = Text_Loader(
            text="", screen=None, font_name="Arial", font_size=10, color=WHITE
        )
        self.tooltip_name = Text_Loader(
            text="", screen=None, font_name="Arial", font_size=14, color=WHITE
        )
        self.tooltip_desc = Text_Loader(
            text="", screen=None, font_name="Arial", font_size=12, color=(200, 200, 200)
        )
        self.tooltip_value = Text_Loader(
            text="", screen=None, font_name="Arial", font_size=12, color=(200, 200, 200)
        )

        self.held_item = None
        self.start_x, self.start_y = SCREENWIDTH - 780 - self.slot_size * self.cols, 610
        self.equip_start_x, self.equip_start_y = self.start_x + 1200, self.start_y - 150

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

    def use_item(self, item_id: str) -> bool:
        """Validates if an item exists and can be consumed/triggered."""
        item = self.get_item(item_id)
        return item is not None

    def draw(self, screen: pygame.Surface) -> None:
        """Renders inventory grid, equipment slots, held item, and tooltips."""
        for i, item in enumerate(self.inventory_slots):
            x = self.start_x + (i % self.cols) * self.slot_size
            y = self.start_y + (i // self.cols) * self.slot_size

            pygame.draw.rect(
                screen, DARK_GRAY, (x, y, self.slot_size, self.slot_size), 1
            )

            if item:
                icon = self._get_icon(item)
                if icon:
                    screen.blit(icon, (x + 5, y + 5))

                if item.quantity > 1:
                    self.quantity_label.update_text(str(item.quantity))
                    screen.blit(
                        self.quantity_label.text_surface,
                        (x + self.slot_size - 15, y + self.slot_size - 15),
                    )

        for i, (slot_name, item) in enumerate(self.equipment_slots.items()):
            ex, ey = self.equip_start_x, self.equip_start_y + i * (self.slot_size + 5)
            pygame.draw.rect(
                screen, (40, 40, 50), (ex, ey, self.slot_size, self.slot_size)
            )

            if item:
                icon = self._get_icon(item)
                screen.blit(icon, (ex + 5, ey + 5))

        if self.held_item:
            mx, my = pygame.mouse.get_pos()
            icon = self._get_icon(self.held_item)
            if icon:
                screen.blit(icon, (mx - self.slot_size // 2, my - self.slot_size // 2))

        if not self.held_item:
            m_pos = pygame.mouse.get_pos()
            idx = self.get_slot_at_mouse(m_pos)
            if idx is not None and self.inventory_slots[idx]:
                self.draw_tooltip(screen, self.inventory_slots[idx], m_pos)

    def draw_tooltip(
        self, screen: pygame.Surface, item: Any, mouse_pos: Tuple[int, int]
    ) -> None:
        """Renders an info box containing item name, description, and value."""
        self.tooltip_name.update_text(item.name)
        self.tooltip_desc.update_text(item.desc)
        self.tooltip_value.update_text(item.value)

        padding, line_spacing = 8, 4
        name_w, name_h = self.tooltip_name.text_surface.get_size()
        desc_w, desc_h = self.tooltip_desc.text_surface.get_size()
        value_w, value_h = self.tooltip_value.text_surface.get_size()

        width = max(name_w, desc_w, value_w if item.value else 0) + (padding * 2)
        height = (
            name_h
            + desc_h
            + (value_h if item.value else 0)
            + (padding * 2)
            + line_spacing
        )

        tx, ty = mouse_pos[0] + 15, mouse_pos[1] + 15
        if tx + width > screen.get_width():
            tx = mouse_pos[0] - width - 5
        if ty + height > screen.get_height():
            ty = mouse_pos[1] - height - 5

        pygame.draw.rect(screen, (20, 20, 20), (tx, ty, width, height))
        pygame.draw.rect(screen, (150, 150, 150), (tx, ty, width, height), 1)

        screen.blit(self.tooltip_name.text_surface, (tx + padding, ty + padding))
        screen.blit(
            self.tooltip_desc.text_surface,
            (tx + padding, ty + padding + name_h + line_spacing),
        )
        if item.value:
            screen.blit(
                self.tooltip_value.text_surface,
                (tx + padding, ty + padding + name_h + desc_h + line_spacing + 4),
            )

    def get_slot_at_mouse(self, mouse_pos: Tuple[int, int]) -> Optional[int]:
        """Calculates which inventory grid index corresponds to the mouse position."""
        mx, my = mouse_pos
        if (
            self.start_x <= mx <= self.start_x + self.cols * self.slot_size
            and self.start_y
            <= my
            <= self.start_y + (self.size // self.cols) * self.slot_size
        ):
            col = (mx - self.start_x) // self.slot_size
            row = (my - self.start_y) // self.slot_size
            index = int(row * self.cols + col)
            return index if 0 <= index < len(self.inventory_slots) else None
        return None

    def get_equip_slot_at_mouse(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Calculates which specific equipment slot name corresponds to the mouse position."""
        mx, my = mouse_pos
        for i, slot_name in enumerate(self.equipment_slots.keys()):
            ex, ey = self.equip_start_x, self.equip_start_y + i * (self.slot_size + 5)
            if pygame.Rect(ex, ey, self.slot_size, self.slot_size).collidepoint(mx, my):
                return slot_name
        return None

    def handle_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Processes item swaps between inventory/equipment slots and the 'held' cursor state."""
        index = self.get_slot_at_mouse(mouse_pos)
        equip_key = self.get_equip_slot_at_mouse(mouse_pos)

        if index is not None:
            temp = self.inventory_slots[index]
            self.inventory_slots[index] = self.held_item
            self.held_item = temp

        elif equip_key is not None:
            if self.held_item:
                if hasattr(self.held_item, "slot") and self.held_item.slot == equip_key:
                    temp = self.equipment_slots[equip_key]
                    self.equipment_slots[equip_key] = self.held_item
                    self.held_item = temp
            else:
                self.held_item = self.equipment_slots[equip_key]
                self.equipment_slots[equip_key] = None

    def get_equipment_bonuses(self) -> Dict[str, float]:
        """Aggregates all stat modifiers provided by currently equipped items."""
        bonuses = {
            "attack": 0,
            "defense": 0,
            "speed": 0,
            "health": 0,
            "speed_multiplier": 0,
        }
        for item in self.equipment_slots.values():
            if item and item.stats:
                for stat, value in item.stats.items():
                    if stat in bonuses:
                        bonuses[stat] += value
        return bonuses

    def _get_icon(self, item: Any) -> Optional[pygame.Surface]:
        """Retrieves or generates a scaled UI icon for the specified item."""
        if not item or not item.image:
            return None
        if not hasattr(item, "ui_icon") or item.ui_icon is None:
            size = self.slot_size - 10
            item.ui_icon = pygame.transform.scale(item.image, (size, size))
        return item.ui_icon
