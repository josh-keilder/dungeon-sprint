import pygame
import globals
from globals import *
from Components.component import Component
from Controllers.sound import SoundController

class InputComponent(Component):
    def __init__(self, node, map):
        super().__init__(node)
        self.node = node
        self.map = map
        
        # --- COOLDOWNS ---
        self.interact_cooldown = 0
        self.pick_up_item_cooldown = 0
        self.healing_cooldown = 0
        self.inventory_cooldown = 0
        self.show_inventory = False

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # System Inputs
        if keys[pygame.K_ESCAPE]:
            self.map.gameStateManager.set_state('options')
            if hasattr(self.map, 'pause_sound'):
                self.map.pause_sound.play()

        # Debug Hitboxes
        if keys[pygame.K_p] and self.interact_cooldown <= 0:
            globals.DEBUG_HITBOXES = not globals.DEBUG_HITBOXES
            self.interact_cooldown = 0.5

        # Healing Logic
        if keys[pygame.K_q] and self.healing_cooldown <= 0:
            health = getattr(self.node, 'health', None)
            inv = getattr(self.node, 'inventory', None)
            if health and inv and health.current < health.max_health:
                if inv.has_item('small_health_potion'):
                    health.heal(SMALL_HEALTH_POTION_VALUE)
                    inv.remove_item('small_health_potion')
                    self.healing_cooldown = 1.0

        # Run Input Methods
        self.movement_input(keys)
        self.interact_input(keys)
        self.inventory_input(keys)

        # Global Cooldown Decay
        if self.healing_cooldown > 0: self.healing_cooldown -= dt
        if self.interact_cooldown > 0: self.interact_cooldown -= dt
        if self.pick_up_item_cooldown > 0: self.pick_up_item_cooldown -= dt
        if self.inventory_cooldown > 0: self.inventory_cooldown -= dt

    def movement_input(self, keys):
        walking = False
        dir_x, dir_y = 0, 0

        if keys[pygame.K_a]: dir_x -= 1; self.node.last_direction = 'left'; walking = True
        if keys[pygame.K_d]: dir_x += 1; self.node.last_direction = 'right'; walking = True
        if keys[pygame.K_w]: dir_y -= 1; self.node.last_direction = 'up'; walking = True
        if keys[pygame.K_s]: dir_y += 1; self.node.last_direction = 'down'; walking = True

        input_vector = pygame.math.Vector2(dir_x, dir_y)
        if input_vector.length_squared() > 0:
            input_vector.normalize_ip()

        # Roll Trigger
        if keys[pygame.K_SPACE] and walking:
            roll = getattr(self.node, 'roll', None)
            if roll and not roll.is_rolling:
                roll.start_roll(input_vector, self.node.last_direction)

        self.node.input_vector = input_vector
        self.node.walking = walking

    def interact_input(self, keys):
        if not keys[pygame.K_f]: return

        # Create a search area around the player to avoid looping through everything
        search_rect = self.node.rect.inflate(15, 15)

        # Chest Interaction
        if self.interact_cooldown <= 0:
            for chest in self.map.chests:
                if search_rect.colliderect(chest.rect):
                    chest.open()
                    self.map.chests.remove(chest)
                    self.interact_cooldown = 0.5
                    return

            # Door Interaction
            inv = getattr(self.node, 'inventory', None)
            if inv and inv.has_item('gold_key'):
                for door in list(self.map.door_tiles):
                    if search_rect.colliderect(door.rect):
                        # Unlock all doors with the same ID
                        id_to_remove = door.door_id
                        self.map.door_tiles = [d for d in self.map.door_tiles if d.door_id != id_to_remove]
                        # Refresh physics tiles in scene
                        self.map.scene.set_wall_tiles(list(self.map.wall_tiles.sprites()) + self.map.door_tiles)
                        inv.remove_item('gold_key')
                        self.interact_cooldown = 0.5
                        return

        # Item Pickup 
        if self.pick_up_item_cooldown <= 0 and self.interact_cooldown <= 0:
            inv = getattr(self.node, 'inventory', None)
            for item in list(self.map.items):
                if search_rect.colliderect(item.rect):
                    if inv:
                        inv.add_item(item.item_data.clone())
                        self.map.items.remove(item)
                        self.pick_up_item_cooldown = 0.2
                        return

    def inventory_input(self, keys):
        if keys[pygame.K_e] and self.inventory_cooldown <= 0:
            self.show_inventory = not self.show_inventory
            self.inventory_cooldown = 0.3

        if self.show_inventory:
            mouse_clicked = pygame.mouse.get_pressed()
            if mouse_clicked[0] and self.inventory_cooldown <= 0:
                inv = getattr(self.node, 'inventory', None)
                if inv:
                    inv.handle_click(pygame.mouse.get_pos())
                    self.inventory_cooldown = 0.2