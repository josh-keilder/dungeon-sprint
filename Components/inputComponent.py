import pygame
import globals
from globals import *
from Components.component import Component
from ui_objects.create_outline import create_outline

class InputComponent(Component):
    def __init__(self, node, map):
        super().__init__(node)

        self.node = node
        self.map = map
        
        self.interact_cooldown = 0
        self.interact_pressed = False

        self.closest_door = None
        self.closest_key = None

        self.show_inventory = False

    def update(self, dt=0):
        keys = pygame.key.get_pressed()

        # Show options menu when in game
        if keys[pygame.K_ESCAPE]:
            self.map.gameStateManager.set_state('options')
            self.map.pause_sound.play()

        # Debug Button
        if keys[pygame.K_p] and self.interact_cooldown <= 0:
            globals.DEBUG_HITBOXES = not globals.DEBUG_HITBOXES
            self.interact_cooldown = 0.5

        self.movement_input(dt, keys)
        self.interact(dt, keys)
        self.inventory_input(dt, keys)


        # Gradual interact delay
        if self.interact_cooldown > 0:
            self.interact_cooldown -= dt

    def movement_input(self, dt, keys):
        walking = False
        dir_x, dir_y = 0 , 0

        # Movement checks
        if keys[pygame.K_a]:
            dir_x -= self.node.movement.speed; self.node.last_direction = 'left'; walking = True
        if keys[pygame.K_d]:
            dir_x += self.node.movement.speed; self.node.last_direction = 'right'; walking = True
        if keys[pygame.K_w]:
            dir_y -= self.node.movement.speed; self.node.last_direction = 'up'; walking = True
        if keys[pygame.K_s]:
            dir_y += self.node.movement.speed; self.node.last_direction = 'down'; walking = True

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

        if self.interact_pressed and self.interact_cooldown <= 0:
            player_pos = self.node.pos
            min_dist = float("inf")
            
            # Unlock Doors (Add key check later)
            for door in self.map.door_tiles:
                dist = player_pos.distance_to(door.pos)
                if dist < UNLOCK_DOOR_DIST and dist < min_dist:
                    self.closest_door = door
                    min_dist = dist
            if self.closest_door:
                self.map.unlock_door(self.closest_door.door_id)
                self.interact_cooldown = 1

            # Pick up keys
            for key in self.map.keys:
                dist = player_pos.distance_to(key.pos)
                if dist < PICK_UP_KEY_DIST and dist < min_dist:
                    self.closest_key = key
                    min_dist = dist
            if self.closest_key:
                print('key picked up')
                self.interact_cooldown = 1
            

    def inventory_input(self, dt, keys):
        # Open Inventory
        if keys[pygame.K_e] and self.interact_cooldown <= 0:
            self.show_inventory = not self.show_inventory
            self.interact_cooldown = 0.5