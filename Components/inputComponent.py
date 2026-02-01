import pygame
import globals
from globals import *
from Components.component import Component
from Controllers.sound import SoundController
from ui_objects.text_loader import Text_Loader

class InputComponent(Component):
    def __init__(self, node, map):
        super().__init__(node)

        # --- ATTRIBUTES ---
        self.node = node
        self.map = map
        
        # --- INTERACT ATTRIBUTES ---
        self.interact_cooldown = 0
        self.interact_pressed = False
        self.pick_up_item_cooldown = 0

        # --- HEALING ATTRIBUTES ---
        self.healing_cooldown = 0

        # --- INVENTORY ATTRIBUTES ---
        self.inventory_cooldown = 0
        self.show_inventory = False

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # Show options menu when in game
        if keys[pygame.K_ESCAPE]:
            self.map.gameStateManager.set_state('options')
            self.map.pause_sound.play()

        # Debug Button
        if keys[pygame.K_p] and self.interact_cooldown <= 0:
            globals.DEBUG_HITBOXES = not globals.DEBUG_HITBOXES
            self.interact_cooldown = 0.5

        if keys[pygame.K_z]:
            SoundController.stop_music(self)

        # Use health potion
        if keys[pygame.K_q] and self.healing_cooldown <= 0 and self.node.health.current < self.node.health.max_health:
            if self.node.inventory.has_item('small_health_potion'):
                self.node.health.current += SMALL_HEALTH_POTION_VALUE
                self.node.inventory.remove_item('small_health_potion')
                self.healing_cooldown = 1

        self.movement_input(dt, keys)
        self.interact(dt, keys)
        self.inventory_input(dt, keys)


        # Gradual cooldown delays
        if self.healing_cooldown > 0:
            self.healing_cooldown -= dt

    def movement_input(self, dt, keys):
        walking = False
        dir_x, dir_y = 0 , 0

        # Movement checks
        if keys[pygame.K_a]:
            dir_x -= self.node.movement.max_speed; self.node.last_direction = 'left'; walking = True
        if keys[pygame.K_d]:
            dir_x += self.node.movement.max_speed; self.node.last_direction = 'right'; walking = True
        if keys[pygame.K_w]:
            dir_y -= self.node.movement.max_speed; self.node.last_direction = 'up'; walking = True
        if keys[pygame.K_s]:
            dir_y += self.node.movement.max_speed; self.node.last_direction = 'down'; walking = True

        input_vector = pygame.math.Vector2(dir_x, dir_y)
        if input_vector.length() > 0:
            input_vector = input_vector.normalize()

        # Roll Check
        if hasattr(self.node, 'roll') and keys[pygame.K_SPACE] and walking and not self.node.roll.is_rolling:
            self.node.roll.start_roll(input_vector, self.node.last_direction)

        self.node.input_vector = input_vector
        self.node.walking = walking

    def interact(self, dt, keys):
        # Checks for interactions between items, doors, etc.
        self.interact_pressed = keys[pygame.K_f]

        player_pos = self.node.pos

        self.closest_door = None
        self.closest_item = None
        self.closest_chest = None

        if self.interact_pressed and self.interact_cooldown <= 0:
            self.open_nearby_chest(player_pos)
            self.open_nearby_door(player_pos)

        if self.interact_pressed and self.pick_up_item_cooldown <= 0:
            self.pick_up_items(player_pos)

        if self.interact_cooldown > 0:
            self.interact_cooldown -= dt
        if self.pick_up_item_cooldown > 0:
            self.pick_up_item_cooldown -= dt

    def pick_up_items(self, player_pos):
        min_dist_item = float("inf")
        # Pick up items
        for item in self.map.items:
            dist = player_pos.distance_to(item.pos)
            if dist < PICK_UP_ITEM_DIST and dist < min_dist_item:
                self.closest_item = item
                min_dist_item = dist

        if self.closest_item:
            # Create a key item and add to inventory
            self.node.inventory.add_item(self.closest_item.item_data.clone())
            # Remove key from map
            self.map.items.remove(self.closest_item)
            self.closest_item = None
            self.pick_up_item_cooldown = 0.2


    def open_nearby_door(self, player_pos):
        min_dist_door = float("inf")
        # Unlock Doors 
        for door in self.map.door_tiles:
            dist = player_pos.distance_to(door.pos)
            if dist < UNLOCK_DOOR_DIST and dist < min_dist_door:
                self.closest_door = door
                min_dist_door = dist
        if self.closest_door:
            # Check to see if player has a key to unlock the door
            if self.node.inventory.has_item('gold_key'):
                # Check door and unlock (remove it)
                for door in list(self.map.door_tiles):
                    if door.door_id == self.closest_door.door_id:
                        self.map.door_tiles.remove(door)
                # Update scene
                self.map.scene.set_wall_tiles(list(self.map.wall_tiles.sprites()) + list(self.map.door_tiles.sprites()))
                self.node.inventory.remove_item(item_id = 'gold_key')
                self.interact_cooldown = 1
                self.closest_door = None

    def open_nearby_chest(self, player_pos):
        min_dist_chest = float("inf")

        for chest in self.map.chests:
            dist = player_pos.distance_to(chest.pos)
            if dist < OPEN_CHEST_DIST and dist < min_dist_chest:
                self.closest_chest = chest
                min_dist_chest = dist
        
        if self.closest_chest:
            self.closest_chest.open()
            self.map.chests.remove(self.closest_chest)
            self.closest_chest = None
            self.interact_cooldown = 1
            self.pick_up_item_cooldown = 0.2

    def inventory_input(self, dt, keys):
        # Open Inventory
        if keys[pygame.K_e] and self.inventory_cooldown <= 0:
            self.show_inventory = not self.show_inventory
            self.inventory_cooldown = 0.5

        self.inventory_cooldown -= dt

        # If inventory is open, listen for clicks
        if self.show_inventory:
            mouse_clicked = pygame.mouse.get_pressed()
            
            # Left Click
            if mouse_clicked[0] and self.inventory_cooldown <= 0:
                mouse_pos = pygame.mouse.get_pos()
                # Call the click handler built in the InventoryComponent
                self.node.inventory.handle_click(mouse_pos)
                
                # Cooldown prevents one click from acting like 60 clicks per second
                self.inventory_cooldown = 0.2
        
        self.inventory_cooldown -= dt
        