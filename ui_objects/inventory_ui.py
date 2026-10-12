import pygame
from globals import SCREENWIDTH, WHITE, DARK_GRAY
from ui_objects.text_loader import Text_Loader


class InventoryUI:
    def __init__(self):
        self.slot_size = 48
        self.cols = 10
        self.start_x, self.start_y = SCREENWIDTH - 780 - self.slot_size * self.cols, 610
        self.equip_start_x, self.equip_start_y = self.start_x + 1200, self.start_y - 150

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

    def draw(self, screen, inventory):
        for i, item in enumerate(inventory.inventory_slots):
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

        for i, (slot_name, item) in enumerate(inventory.equipment_slots.items()):
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
            idx = self.get_slot_at_mouse(m_pos, inventory)
            if idx is not None and inventory.inventory_slots[idx]:
                self.draw_tooltip(screen, inventory.inventory_slots[idx], m_pos)

    def draw_tooltip(self, screen, item, mouse_pos):
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

    def get_slot_at_mouse(self, mouse_pos, inventory):
        mx, my = mouse_pos
        if (
            self.start_x <= mx <= self.start_x + self.cols * self.slot_size
            and self.start_y
            <= my
            <= self.start_y
            + (len(inventory.inventory_slots) // self.cols) * self.slot_size
        ):
            col = (mx - self.start_x) // self.slot_size
            row = (my - self.start_y) // self.slot_size
            index = int(row * self.cols + col)
            return index if 0 <= index < len(inventory.inventory_slots) else None
        return None

    def get_equip_slot_at_mouse(self, mouse_pos, inventory):
        mx, my = mouse_pos
        for i, slot_name in enumerate(inventory.equipment_slots.keys()):
            ex, ey = self.equip_start_x, self.equip_start_y + i * (self.slot_size + 5)
            if pygame.Rect(ex, ey, self.slot_size, self.slot_size).collidepoint(mx, my):
                return slot_name
        return None

    def handle_click(self, mouse_pos, inventory):
        index = self.get_slot_at_mouse(mouse_pos, inventory)
        equip_key = self.get_equip_slot_at_mouse(mouse_pos, inventory)

        if index is not None:
            temp = inventory.inventory_slots[index]
            inventory.inventory_slots[index] = self.held_item
            self.held_item = temp

        elif equip_key is not None:
            if self.held_item:
                if hasattr(self.held_item, "slot") and self.held_item.slot == equip_key:
                    temp = inventory.equipment_slots[equip_key]
                    inventory.equipment_slots[equip_key] = self.held_item
                    self.held_item = temp
            else:
                self.held_item = inventory.equipment_slots[equip_key]
                inventory.equipment_slots[equip_key] = None

    def _get_icon(self, item):
        if not item or not item.image:
            return None
        if not hasattr(item, "ui_icon") or item.ui_icon is None:
            size = self.slot_size - 10
            item.ui_icon = pygame.transform.scale(item.image, (size, size))
        return item.ui_icon
