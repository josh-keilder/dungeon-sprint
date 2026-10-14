import random

import pygame

from Entities.enemies.load_enemies import load_enemies
from Entities.player.load_player import load_player
from globals import UNLOCK_DOOR_DISTANCE, WHITE
from items.itemDataBase import initialize_item_database
from items.items import WorldItem
from states.map.map_loader import load_level_data
from systems import debug, interact, sound
from systems.camera import camera, center_camera, is_on_screen
from systems.collision import find_player_contacts
from systems.combat import resolve_contact
from systems.health import is_dead
from systems.hitbox import draw_hitbox
from systems.input import read_input
from ui_objects.health_bar import draw_health_bar
from ui_objects.inventory_ui import InventoryUI

LOOT_SCATTER_X = 10
LOOT_SCATTER_Y = 5

PLAYER_HEALTH_BAR_POS = (20, 20)
PLAYER_HEALTH_BAR_SIZE = (200, 10)


class Level:
    def __init__(self, game_state_manager, map_path):
        self.game_state_manager = game_state_manager

        # Ground items, spawned during play
        self.ground_items = pygame.sprite.Group()

        # Item templates and map data
        self.item_database = initialize_item_database()

        level_data = load_level_data(map_path)
        self.map_surface = level_data["map_surface"]
        self.decor_tiles = level_data["decor_tiles"]
        self.wall_tiles = level_data["wall_tiles"]
        self.door_tiles = level_data["door_tiles"]
        self.chests = level_data["chests"]

        # Player Setup
        self.player = load_player(level_data["player_spawn"])
        center_camera(self.player.rect.center)

        # Enemy Spawning
        self.enemies = load_enemies(level_data["enemy_spawns"])

        # Everything that blocks movement: walls and locked doors
        self.solid_tiles = []
        self.refresh_walls()

        self.show_inventory = False
        self.inventory_ui = InventoryUI()

    def update(self, dt):

        self.player.intent = read_input()

        if self.player.intent["pause"]:
            self.game_state_manager.set_state("options")
            sound.play_sfx("Pause")
            return

        if self.player.intent["debug"]:
            debug.toggle_hitboxes()

        if self.player.intent["interact"]:
            interact.interact(self.player, self)

        if self.player.intent["inventory"]:
            if self.show_inventory:
                if self.inventory_ui.return_held_item(self.player.inventory):
                    self.show_inventory = False
            else:
                self.show_inventory = True

        if self.show_inventory and self.player.intent["mouse_left_click"] is not None:
            self.inventory_ui.handle_click(
                self.player.intent["mouse_left_click"], self.player.inventory
            )

        self.player.update(dt, self.solid_tiles)
        for enemy in self.enemies:
            enemy.update(dt, self.solid_tiles, self.player.pos)

        contacts = find_player_contacts(self.player, self.enemies)

        for enemy in contacts:
            resolve_contact(self.player, enemy)

            if is_dead(enemy.health):
                self.enemies.remove(enemy)

        self.ground_items.update(dt)
        center_camera(self.player.rect.center)

    def draw(self, screen):
        # Floor
        screen.blit(self.map_surface, (-camera.x, -camera.y))

        # Static tiles: decor, walls, doors
        for group in [self.decor_tiles, self.wall_tiles, self.door_tiles]:
            for sprite in group:
                if is_on_screen(sprite.rect):
                    sprite.draw(screen)

                    # Highlight doors when player is nearby
                    if group == self.door_tiles:
                        if sprite.pos.distance_to(self.player.pos) < UNLOCK_DOOR_DISTANCE:
                            draw_hitbox(
                                screen, sprite.image, sprite.rect, camera, WHITE
                            )

        # Ground items and chests
        for group in [self.ground_items, self.chests]:
            for obj in group:
                if is_on_screen(obj.rect):
                    obj.draw(screen, camera)

        # Actors, sorted by y so lower ones draw on top
        actors = [self.player] + self.enemies
        actors = sorted(actors, key=lambda actor: actor.rect.y)

        for actor in actors:
            if is_on_screen(actor.rect):
                actor.draw(screen, camera)

        draw_health_bar(
            screen, self.player.health, *PLAYER_HEALTH_BAR_POS, *PLAYER_HEALTH_BAR_SIZE
        )

        if self.show_inventory:
            self.inventory_ui.draw(screen, self.player.inventory)

    def unlock_door(self, door_id):
        for door in self.door_tiles.sprites():
            if door.door_id == door_id:
                door.kill()

        self.refresh_walls()

    def refresh_walls(self):
        self.solid_tiles = list(self.wall_tiles) + list(self.door_tiles)

    def spawn_loot(self, drops, center):
        for item_id, quantity in drops:
            item_data = self.item_database[item_id]
            offset_x = random.randint(-LOOT_SCATTER_X, LOOT_SCATTER_X)
            offset_y = random.randint(-LOOT_SCATTER_Y, LOOT_SCATTER_Y)

            WorldItem(
                groups=self.ground_items,
                pos=(center[0] + offset_x, center[1] + offset_y),
                item_data=item_data,
                quantity=quantity,
            )
