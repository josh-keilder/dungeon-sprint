import math

import pygame

from globals import (
    FONT_PATH,
    GAME_SCALE,
    PALETTE_STEEL,
    PALETTE_STONE,
    PALETTE_TORCH,
    PALETTE_VOID,
    PANEL_FRAME_PATH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from systems.assets import load_image
from systems.inventory import add_item, can_equip
from ui_components.panel import make_panel
from ui_components.text_label import TextLabel

# Window layout
INVENTORY_FONT_SIZE = 24
SLOT_SIZE = 72
SLOT_GAP = 6
SLOT_ICON_OFFSET = 12
GRID_COLUMNS = 5
WINDOW_PADDING = 24
EQUIPMENT_GAP = 24
TITLE_HEIGHT = 36

# Tooltip
TOOLTIP_PADDING = 18
TOOLTIP_LINE_HEIGHT = 27
TOOLTIP_MOUSE_OFFSET = 18

INVENTORY_DIM_ALPHA = 120


class InventoryUI:
    def __init__(self, inventory):
        self.tooltip_cache = {}
        self.icon_cache = {}

        self.held_item = None

        slot_count = len(inventory["slots"])
        equipment_names = list(inventory["equipment"].keys())

        grid_rows = math.ceil(slot_count / GRID_COLUMNS)
        grid_width = GRID_COLUMNS * SLOT_SIZE + (GRID_COLUMNS - 1) * SLOT_GAP
        grid_height = grid_rows * SLOT_SIZE + (grid_rows - 1) * SLOT_GAP
        equipment_height = (
            len(equipment_names) * SLOT_SIZE + (len(equipment_names) - 1) * SLOT_GAP
        )

        window_width = (
            WINDOW_PADDING + SLOT_SIZE + EQUIPMENT_GAP + grid_width + WINDOW_PADDING
        )
        window_height = (
            WINDOW_PADDING
            + TITLE_HEIGHT
            + max(grid_height, equipment_height)
            + WINDOW_PADDING
        )
        self.window_pos = (
            SCREEN_WIDTH - window_width
        ) // 2 // GAME_SCALE * GAME_SCALE, (
            SCREEN_HEIGHT - window_height
        ) // 2 // GAME_SCALE * GAME_SCALE

        self.frame_image = load_image(PANEL_FRAME_PATH)
        self.window_panel = make_panel(self.frame_image, (window_width, window_height))
        self.slot_panel = make_panel(self.frame_image, (SLOT_SIZE, SLOT_SIZE))

        slots_top = self.window_pos[1] + WINDOW_PADDING + TITLE_HEIGHT
        equipment_x = self.window_pos[0] + WINDOW_PADDING
        grid_x = equipment_x + SLOT_SIZE + EQUIPMENT_GAP

        self.grid_slot_rects = [
            pygame.Rect(
                grid_x + column * (SLOT_SIZE + SLOT_GAP),
                slots_top + row * (SLOT_SIZE + SLOT_GAP),
                SLOT_SIZE,
                SLOT_SIZE,
            )
            for row, column in (
                divmod(index, GRID_COLUMNS) for index in range(slot_count)
            )
        ]
        self.equipment_slot_rects = {
            slot_name: pygame.Rect(
                equipment_x,
                slots_top + position * (SLOT_SIZE + SLOT_GAP),
                SLOT_SIZE,
                SLOT_SIZE,
            )
            for position, slot_name in enumerate(equipment_names)
        }

        self.font = pygame.font.Font(FONT_PATH, INVENTORY_FONT_SIZE)

        self.title_label = TextLabel(
            "INVENTORY",
            color=PALETTE_STEEL,
            font=self.font,
        )
        title_x = (
            self.window_pos[0]
            + (window_width - self.title_label.text_surface.get_width()) // 2
        )
        self.title_label.pos = (title_x, self.window_pos[1] + WINDOW_PADDING // 2)

        self.count_label = TextLabel(
            "", color=PALETTE_STEEL, font=self.font, outline_color=PALETTE_VOID
        )

        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, INVENTORY_DIM_ALPHA))

    def draw(self, screen, inventory):
        screen.blit(self.overlay, (0, 0))
        screen.blit(self.window_panel, self.window_pos)

        self.title_label.draw(screen)

        for slot_index, rect in enumerate(self.grid_slot_rects):
            self.draw_slot(screen, rect, inventory["slots"][slot_index])

        for slot_name, rect in self.equipment_slot_rects.items():
            self.draw_slot(screen, rect, inventory["equipment"][slot_name])

        if self.held_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            icon = self._get_icon(self.held_item)
            if icon:
                screen.blit(
                    icon,
                    (mouse_x - icon.get_width() // 2, mouse_y - icon.get_height() // 2),
                )

        if not self.held_item:
            mouse_pos = pygame.mouse.get_pos()
            slot_index = self.get_slot_at_mouse(mouse_pos)
            equipment_name = self.get_equipment_slot_at_mouse(mouse_pos)

            hovered_item = None
            if slot_index is not None:
                hovered_item = inventory["slots"][slot_index]
            elif equipment_name is not None:
                hovered_item = inventory["equipment"][equipment_name]

            tooltip = None
            if hovered_item is not None:
                lines = [
                    (hovered_item.name, PALETTE_STEEL),
                    (hovered_item.description, PALETTE_STONE),
                ]
                if hovered_item.value_text:
                    lines.append((hovered_item.value_text, PALETTE_TORCH))

                tooltip = self.get_tooltip(hovered_item.id, lines)

            elif equipment_name is not None:
                tooltip = self.get_tooltip(
                    f"empty_{equipment_name}", [(equipment_name.title(), PALETTE_STONE)]
                )

            if tooltip is not None:
                self.draw_tooltip(screen, tooltip, mouse_pos)

    def draw_slot(self, screen, rect, item):
        screen.blit(self.slot_panel, rect.topleft)

        if item is None:
            return

        icon = self._get_icon(item)
        screen.blit(icon, (rect.x + SLOT_ICON_OFFSET, rect.y + SLOT_ICON_OFFSET))

        if item.quantity > 1:
            self.count_label.update_text(str(item.quantity))
            count_bounds = self.count_label.text_surface.get_bounding_rect()
            self.count_label.pos = (
                rect.right - count_bounds.right - GAME_SCALE,
                rect.bottom - count_bounds.bottom - GAME_SCALE,
            )
            self.count_label.draw(screen)

    def draw_tooltip(self, screen, tooltip, mouse_pos):
        tooltip_x = mouse_pos[0] + TOOLTIP_MOUSE_OFFSET
        tooltip_y = mouse_pos[1] + TOOLTIP_MOUSE_OFFSET

        if tooltip_x + tooltip.get_width() > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - TOOLTIP_MOUSE_OFFSET - tooltip.get_width()

        if tooltip_y + tooltip.get_height() > SCREEN_HEIGHT:
            tooltip_y = mouse_pos[1] - TOOLTIP_MOUSE_OFFSET - tooltip.get_height()

        screen.blit(tooltip, (tooltip_x, tooltip_y))

    def build_tooltip(self, lines):
        rendered_lines = [self.font.render(text, False, color) for text, color in lines]

        ink_top = rendered_lines[0].get_bounding_rect().top
        ink_height = rendered_lines[0].get_bounding_rect().height

        width = max(line.get_width() for line in rendered_lines) + 2 * TOOLTIP_PADDING
        height = (
            2 * TOOLTIP_PADDING
            + (len(rendered_lines) - 1) * TOOLTIP_LINE_HEIGHT
            + ink_height
        )

        width = math.ceil(width / GAME_SCALE) * GAME_SCALE
        height = math.ceil(height / GAME_SCALE) * GAME_SCALE

        tooltip = make_panel(self.frame_image, (width, height))

        for line_index, line in enumerate(rendered_lines):
            tooltip.blit(
                line,
                (
                    TOOLTIP_PADDING,
                    TOOLTIP_PADDING - ink_top + line_index * TOOLTIP_LINE_HEIGHT,
                ),
            )

        return tooltip

    def get_tooltip(self, key, lines):
        if key not in self.tooltip_cache:
            self.tooltip_cache[key] = self.build_tooltip(lines)

        return self.tooltip_cache[key]

    def get_slot_at_mouse(self, mouse_pos):
        for slot_index, rect in enumerate(self.grid_slot_rects):
            if rect.collidepoint(mouse_pos):
                return slot_index

        return None

    def get_equipment_slot_at_mouse(self, mouse_pos):
        for slot_index, rect in self.equipment_slot_rects.items():
            if rect.collidepoint(mouse_pos):
                return slot_index

        return None

    def handle_click(self, mouse_pos, inventory):
        slot_index = self.get_slot_at_mouse(mouse_pos)
        equipment_slot_name = self.get_equipment_slot_at_mouse(mouse_pos)

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
            self.icon_cache[item.id] = pygame.transform.scale_by(item.image, GAME_SCALE)

        return self.icon_cache[item.id]
