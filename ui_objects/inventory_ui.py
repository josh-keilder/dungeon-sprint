import pygame

from globals import DARK_GRAY, SCREEN_WIDTH, WHITE
from systems.inventory import add_item, can_equip
from ui_objects.text_label import TextLabel


class InventoryUI:
    def __init__(self):
        self.slot_size = 48
        self.columns = 10
        self.grid_start_x, self.grid_start_y = SCREEN_WIDTH - 780 - self.slot_size * self.columns, 610
        self.equipment_start_x, self.equipment_start_y = self.grid_start_x + 1200, self.grid_start_y - 150

        self.quantity_label = TextLabel(
            text="", font_name="Arial", font_size=10, color=WHITE
        )
        self.tooltip_name = TextLabel(
            text="", font_name="Arial", font_size=14, color=WHITE
        )
        self.tooltip_description = TextLabel(
            text="", font_name="Arial", font_size=12, color=(200, 200, 200)
        )
        self.tooltip_value = TextLabel(
            text="", font_name="Arial", font_size=12, color=(200, 200, 200)
        )

        self.held_item = None

        self.icon_cache = {}

    def draw(self, screen, inventory):
        for slot_index, item in enumerate(inventory["slots"]):
            x = self.grid_start_x + (slot_index % self.columns) * self.slot_size
            y = self.grid_start_y + (slot_index // self.columns) * self.slot_size

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

        for slot_index, (slot_name, item) in enumerate(inventory["equipment"].items()):
            equipment_slot_x, equipment_slot_y = self.equipment_start_x, self.equipment_start_y + slot_index * (self.slot_size + 5)
            pygame.draw.rect(
                screen, (40, 40, 50), (equipment_slot_x, equipment_slot_y, self.slot_size, self.slot_size)
            )

            if item:
                icon = self._get_icon(item)
                screen.blit(icon, (equipment_slot_x + 5, equipment_slot_y + 5))

        if self.held_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            icon = self._get_icon(self.held_item)
            if icon:
                screen.blit(icon, (mouse_x - self.slot_size // 2, mouse_y - self.slot_size // 2))

        if not self.held_item:
            mouse_pos = pygame.mouse.get_pos()
            slot_index = self.get_slot_at_mouse(mouse_pos, inventory)
            if slot_index is not None and inventory["slots"][slot_index]:
                self.draw_tooltip(screen, inventory["slots"][slot_index], mouse_pos)

    def draw_tooltip(self, screen, item, mouse_pos):
        self.tooltip_name.update_text(item.name)
        self.tooltip_description.update_text(item.description)
        self.tooltip_value.update_text(item.value_text)

        padding, line_spacing = 8, 4
        name_width, name_height = self.tooltip_name.text_surface.get_size()
        description_width, description_height = self.tooltip_description.text_surface.get_size()
        value_width, value_height = self.tooltip_value.text_surface.get_size()

        width = max(name_width, description_width, value_width if item.value_text else 0) + (padding * 2)
        height = (
            name_height
            + description_height
            + (value_height if item.value_text else 0)
            + (padding * 2)
            + line_spacing
        )

        tooltip_x, tooltip_y = mouse_pos[0] + 15, mouse_pos[1] + 15
        if tooltip_x + width > screen.get_width():
            tooltip_x = mouse_pos[0] - width - 5
        if tooltip_y + height > screen.get_height():
            tooltip_y = mouse_pos[1] - height - 5

        pygame.draw.rect(screen, (20, 20, 20), (tooltip_x, tooltip_y, width, height))
        pygame.draw.rect(screen, (150, 150, 150), (tooltip_x, tooltip_y, width, height), 1)

        screen.blit(self.tooltip_name.text_surface, (tooltip_x + padding, tooltip_y + padding))
        screen.blit(
            self.tooltip_description.text_surface,
            (tooltip_x + padding, tooltip_y + padding + name_height + line_spacing),
        )
        if item.value_text:
            screen.blit(
                self.tooltip_value.text_surface,
                (tooltip_x + padding, tooltip_y + padding + name_height + description_height + line_spacing + 4),
            )

    def get_slot_at_mouse(self, mouse_pos, inventory):
        mouse_x, mouse_y = mouse_pos
        if (
            self.grid_start_x <= mouse_x <= self.grid_start_x + self.columns * self.slot_size
            and self.grid_start_y
            <= mouse_y
            <= self.grid_start_y + (len(inventory["slots"]) // self.columns) * self.slot_size
        ):
            column = (mouse_x - self.grid_start_x) // self.slot_size
            row = (mouse_y - self.grid_start_y) // self.slot_size
            slot_index = int(row * self.columns + column)
            return slot_index if 0 <= slot_index < len(inventory["slots"]) else None
        return None

    def get_equipment_slot_at_mouse(self, mouse_pos, inventory):
        mouse_x, mouse_y = mouse_pos
        for slot_index, slot_name in enumerate(inventory["equipment"].keys()):
            equipment_slot_x, equipment_slot_y = self.equipment_start_x, self.equipment_start_y + slot_index * (self.slot_size + 5)
            if pygame.Rect(equipment_slot_x, equipment_slot_y, self.slot_size, self.slot_size).collidepoint(mouse_x, mouse_y):
                return slot_name
        return None

    def handle_click(self, mouse_pos, inventory):
        slot_index = self.get_slot_at_mouse(mouse_pos, inventory)
        equipment_slot_name = self.get_equipment_slot_at_mouse(mouse_pos, inventory)

        if slot_index is not None:
            swapped_item = inventory["slots"][slot_index]
            inventory["slots"][slot_index] = self.held_item
            self.held_item = swapped_item

        elif equipment_slot_name is not None:
            if self.held_item:
                if can_equip(self.held_item, equipment_slot_name):
                    swapped_item = inventory["equipment"][equipment_slot_name]
                    inventory["equipment"][equipment_slot_name] = self.held_item
                    self.held_item = swapped_item
            else:
                self.held_item = inventory["equipment"][equipment_slot_name]
                inventory["equipment"][equipment_slot_name] = None

    def return_held_item(self, inventory):
        if self.held_item is None:
            return True

        leftover = add_item(inventory, self.held_item)

        if leftover == 0:
            self.held_item = None
            return True

        return False

    def _get_icon(self, item):
        if not item or not item.image:
            return None

        if item.id not in self.icon_cache:
            icon_size = self.slot_size - 10
            self.icon_cache[item.id] = pygame.transform.scale(item.image, (icon_size, icon_size))

        return self.icon_cache[item.id]
