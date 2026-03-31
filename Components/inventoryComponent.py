import pygame
from globals import *
from Components.component import Component
from ui_objects.text_loader import Text_Loader
from items.items import EquipmentItem


class InventoryComponent(Component):
    def __init__(self, node, size, cols=10):
        self.node = node
        self.size = size
        self.cols = cols
        self.inventory_slots = [None] * size
        self.slot_size = 48  # Adjust for inventory size on screen
        self.padding = 2

        self.equipment_slots = {
            "head": None,
            "chest": None,
            "boots": None,
            "ability_1": None,
            "ability_2": None,
        }

        # Quantity attributes
        self.quantity_label = Text_Loader(
            text="", screen=None, font_name="Arial", font_size=10, color=WHITE
        )

        # Tool tip attributes
        self.tooltip_name = Text_Loader(
            text="", screen=None, font_name="Arial", font_size=14, color=WHITE
        )
        self.tooltip_desc = Text_Loader(
            text="", screen=None, font_name="Arial", font_size=12, color=(200, 200, 200)
        )
        self.tooltip_value = Text_Loader(
            text="", screen=None, font_name="Arial", font_size=12, color=(200, 200, 200)
        )

        # State for moving items
        self.held_item = None

        self.start_x, self.start_y = SCREENWIDTH - 780 - self.slot_size * self.cols, 610

        self.equip_start_x, self.equip_start_y = self.start_x + 1200, self.start_y - 150

    def add_item(self, item):
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
                    # Clone the item so the inventory owns a unique copy
                    self.inventory_slots[i] = item.clone()
                    return True

        return False

    def remove_item(self, item_id, quantity=1):
        # First, check if the player even has enough total across all stacks
        total_found = sum(
            slot.quantity
            for slot in self.inventory_slots
            if slot and slot.id == item_id
        )

        if total_found < quantity:
            return False  # Not enough items to remove

        # Start removing
        remaining_to_remove = quantity
        for i in range(len(self.inventory_slots)):
            slot = self.inventory_slots[i]

            if slot and slot.id == item_id:
                if slot.quantity > remaining_to_remove:
                    # This stack has more than we need, just subtract and stop
                    slot.quantity -= remaining_to_remove
                    remaining_to_remove = 0
                    break
                else:
                    # This stack is smaller or equal to what we need
                    remaining_to_remove -= slot.quantity
                    self.inventory_slots[i] = None  # Empty the slot

                if remaining_to_remove <= 0:
                    break

        return True

    def get_item(self, item_id):
        for slot in self.inventory_slots:
            if slot and slot.id == item_id:
                return slot
        return None

    def has_item(self, item_id, quantity=1):
        item = self.get_item(item_id)
        return item and item.quantity >= quantity

    def use_item(self, item_id):
        item = self.get_item(item_id)
        if item:
            return True
        return False

    def draw(self, screen):
        for i, item in enumerate(self.inventory_slots):
            x = self.start_x + (i % self.cols) * self.slot_size
            y = self.start_y + (i // self.cols) * self.slot_size

            # Slot Backdrop
            pygame.draw.rect(
                screen, DARK_GRAY, (x, y, self.slot_size, self.slot_size), 1
            )

            if item:
                icon = self._get_icon(item)
                if icon:
                    screen.blit(icon, (x + 5, y + 5))

                # Quantity Text
                if item.quantity > 1:
                    self.quantity_label.update_text(str(item.quantity))
                    screen.blit(
                        self.quantity_label.text_surface,
                        (x + self.slot_size - 15, y + self.slot_size - 15),
                    )

        # Draw Equipment
        for i, (slot_name, item) in enumerate(self.equipment_slots.items()):
            ex, ey = self.equip_start_x, self.equip_start_y + i * (self.slot_size + 5)
            pygame.draw.rect(
                screen, (40, 40, 50), (ex, ey, self.slot_size, self.slot_size)
            )

            if item:
                icon = self._get_icon(item)
                screen.blit(icon, (ex + 5, ey + 5))

        # Draw Held Item (Drag and Drop)
        if self.held_item:
            mx, my = pygame.mouse.get_pos()
            icon = self._get_icon(self.held_item)
            screen.blit(icon, (mx - self.slot_size // 2, my - self.slot_size // 2))

        # Tooltips (Only if not dragging)
        if not self.held_item:
            m_pos = pygame.mouse.get_pos()
            idx = self.get_slot_at_mouse(m_pos)
            if idx is not None and self.inventory_slots[idx]:
                self.draw_tooltip(screen, self.inventory_slots[idx], m_pos)

    def draw_tooltip(self, screen, item, mouse_pos):
        if not item:
            return

        # Update the text surfaces with current item data
        self.tooltip_name.update_text(item.name)
        self.tooltip_desc.update_text(item.desc)

        self.tooltip_value.update_text(item.value)

        # Calculate dimensions
        padding = 8
        line_spacing = 4
        name_w = self.tooltip_name.text_surface.get_width()
        name_h = self.tooltip_name.text_surface.get_height()
        desc_w = self.tooltip_desc.text_surface.get_width()
        desc_h = self.tooltip_desc.text_surface.get_height()
        value_w = self.tooltip_value.text_surface.get_width()
        value_h = self.tooltip_value.text_surface.get_height()

        if not item.value:
            width = max(name_w, desc_w) + (padding * 2)
            height = name_h + desc_h + (padding * 2) + line_spacing
        else:
            width = max(name_w, desc_w, value_w) + (padding * 2)
            height = name_h + desc_h + value_h + (padding * 2) + line_spacing

        # Offset from cursor
        tx, ty = mouse_pos[0] + 15, mouse_pos[1] + 15

        # Boundary check: Keep tooltip on screen
        if tx + width > screen.get_width():
            tx = mouse_pos[0] - width - 5
        if ty + height > screen.get_height():
            ty = mouse_pos[1] - height - 5

        pygame.draw.rect(screen, (20, 20, 20), (tx, ty, width, height))
        pygame.draw.rect(screen, (150, 150, 150), (tx, ty, width, height), 1)  # Border

        screen.blit(self.tooltip_name.text_surface, (tx + padding, ty + padding))
        screen.blit(
            self.tooltip_desc.text_surface,
            (tx + padding, ty + padding + name_h + line_spacing),
        )
        screen.blit(
            self.tooltip_value.text_surface,
            (tx + padding, ty + padding + name_h + desc_h + line_spacing + 4),
        )

    def get_slot_at_mouse(self, mouse_pos):
        mx, my = mouse_pos

        # Check if mouse is within the inventory grid bounds
        if (
            self.start_x <= mx <= self.start_x + self.cols * self.slot_size
            and self.start_y
            <= my
            <= self.start_y + (self.size // self.cols) * self.slot_size
        ):

            col = (mx - self.start_x) // self.slot_size
            row = (my - self.start_y) // self.slot_size
            index = int(row * self.cols + col)

            if 0 <= index < len(self.inventory_slots):
                return index
        return None

    def get_equip_slot_at_mouse(self, mouse_pos):
        mx, my = mouse_pos

        # Iterate through the keys (head, chest, etc.) and their index
        for i, slot_name in enumerate(self.equipment_slots.keys()):
            # Calculate the exact box for THIS specific equipment slot
            # This MUST match the math used in the draw() method
            ex = self.equip_start_x
            ey = self.equip_start_y + i * (self.slot_size + 5)

            # Create a temporary rect to check collision
            slot_rect = pygame.Rect(ex, ey, self.slot_size, self.slot_size)

            if slot_rect.collidepoint(mx, my):
                return slot_name  # Returns 'head', 'chest', etc.

        return None

    def handle_click(self, mouse_pos):
        index = self.get_slot_at_mouse(mouse_pos)

        equip_key = self.get_equip_slot_at_mouse(mouse_pos)

        if index is not None:
            # If we are holding an item
            if self.held_item:
                # Swap held item with whatever is in the slot (even if None)
                temp = self.inventory_slots[index]
                self.inventory_slots[index] = self.held_item
                self.held_item = temp
            else:
                # If not holding anything, pick up the item in the slot
                self.held_item = self.inventory_slots[index]
                self.inventory_slots[index] = None

        elif equip_key is not None:
            if self.held_item:
                if hasattr(self.held_item, "slot") and self.held_item.slot == equip_key:
                    temp = self.equipment_slots[equip_key]
                    self.equipment_slots[equip_key] = self.held_item
                    self.held_item = temp

            else:
                # If not holding anything, pick up the item in the slot
                self.held_item = self.equipment_slots[equip_key]
                self.equipment_slots[equip_key] = None

    def get_equipment_bonuses(self):
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

    def _get_icon(self, item):
        if not item or not item.image:
            return None

        # Check if the item already has a cached UI icon
        if not hasattr(item, "ui_icon") or item.ui_icon is None:
            # Scale once and store it on the item instance
            size = self.slot_size - 10
            item.ui_icon = pygame.transform.scale(item.image, (size, size))
        return item.ui_icon
