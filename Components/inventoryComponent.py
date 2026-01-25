import pygame
from globals import *
from Components.component import Component
from ui_objects.text_loader import Text_Loader
import copy

class Item:
    def __init__(self, id, type= None, name=None, image= None, desc = None, quantity = 1, max_stack= 99):
        self.id = id
        self.type = type
        self.name = name
        self.image = image
        self.desc = desc
        self.quantity = quantity
        self.max_stack = max_stack

    def clone(self):
        return copy.copy(self)


class InventoryComponent(Component):
    def __init__(self, node, size, cols = 10):
        self.node = node
        self.size = size
        self.cols = cols
        self.inventory_slots = [None] * size
        self.slot_size = 40
        self.padding = 2

        self.quantity_label = Text_Loader(text="", screen=None, font_size=18, color=WHITE)
        

    def add_item(self, item):
        for slot in self.inventory_slots:
            if slot and slot.id == item.id:
                space_available = slot.max_stack - slot.quantity
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
        for i, slot in enumerate(self.inventory_slots):
            if slot and slot.id == item_id:
                slot.quantity -= quantity
                if slot.quantity <= 0:
                    self.inventory_slots[i] = None
                return True
        return False
    
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
        start_x, start_y = screen.get_width() - 10 - self.slot_size * self.cols, 10
        
        for i, slot in enumerate(self.inventory_slots):
            x = start_x + (i % self.cols) * self.slot_size
            y = start_y + (i // self.cols) * self.slot_size
            
            pygame.draw.rect(screen, (100, 100, 100), (x, y, self.slot_size, self.slot_size), 2)
            
            if slot:
                if slot.image:
                    screen.blit(slot.image, (x + 5, y + 5))
                
                if slot.quantity > 1:
                    # Update the loader's internal state
                    self.quantity_label.update_text(str(slot.quantity))
                    
                    # Manual blit using the loader's surface at the calculated grid position
                    # We offset it to the bottom-right of the current slot
                    text_pos = (x + self.slot_size - 18, y + self.slot_size - 18)
                    screen.blit(self.quantity_label.text_surface, text_pos)