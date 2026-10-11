"""
State: Dungeon Level One
------------------------
Manages the primary gameplay state for the first dungeon level. This class
handles Tiled map loading (.tmx), entity spawning (player/enemies),
camera tracking, and the rendering order of world objects.

Classes:
    Dungeon_Level_One: The controller for the first playable dungeon area.
"""

import pygame
from globals import *
import globals
from pytmx.util_pygame import load_pygame
from states.map.tiles import WallTile, DecorTile, Door
from Entities.player.load_player import load_player
from ui_objects.camera import camera_update, camera, is_on_screen
from Entities.enemies.load_enemies import load_enemies
from states.scene import Scene
from items.items import Chest, WorldItem
from items.itemDataBase import initialize_item_database

from systems.input import read_input
from systems import sound, interact

pygame.mixer.init()


class Dungeon_Level_One:
    def __init__(self, screen, gameStateManager, file_path=None):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.file_path = DUNGEON_LEVEL_ONE

        # Scene and Entity Management
        self.scene = Scene()
        self.sprites = pygame.sprite.Group()
        self.wall_tiles = pygame.sprite.Group()
        self.door_tiles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.chests = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.enemies_group = pygame.sprite.Group()

        # Data Initialization
        self.ITEM_DATABASE = initialize_item_database()
        self.load_map(file_path=self.file_path)

        # Player Setup
        self.player = load_player(map=self)
        self.scene.add_child(self.player)

        # Enemy Spawning
        self.enemies = load_enemies(player=self.player, file_path=self.file_path)
        for enemy in self.enemies:
            self.scene.add_child(enemy)

        # Collision Setup: Combine static walls and interactable doors
        self.scene.set_wall_tiles(list(self.wall_tiles) + list(self.door_tiles))

        self.show_inventory = False

    def update(self, dt):
        """Updates all world entities and syncs the camera focal point."""

        self.player.intent = read_input()

        if self.player.intent["pause"]:
            self.gameStateManager.set_state("options")
            sound.play_sfx("Pause")
            return

        if self.player.intent["debug"]:
            globals.DEBUG_HITBOXES = not globals.DEBUG_HITBOXES

        if self.player.intent["interact"]:
            interact.interact(self.player, self)

        if self.player.intent["inventory"]:
            self.show_inventory = not self.show_inventory

        if self.show_inventory and self.player.intent["mouse_left_click"] is not None:
            self.player.inventory.handle_click(self.player.intent["mouse_left_click"])

        self.scene.update(dt)
        self.items.update(dt)
        self.sprites.update(dt)
        camera_update(self.player)

    def draw(self):
        """Renders the world layers, applying camera offsets and culling."""
        # Background / Floor
        self.screen.blit(self.map_surface, (-camera.x, -camera.y))

        # Static Tiles & Decorations
        for group in [self.sprites, self.wall_tiles, self.door_tiles]:
            for sprite in group:
                if is_on_screen(sprite.rect):
                    sprite.draw(self.screen)

                    # Highlight doors when player is nearby
                    if group == self.door_tiles:
                        if sprite.pos.distance_to(self.player.pos) < UNLOCK_DOOR_DIST:
                            sprite.hitbox.draw(
                                self.screen, camera=camera, color=WHITE, skip_debug=True
                            )

        # Interactive Objects
        for group in [self.items, self.chests]:
            for obj in group:
                if is_on_screen(obj.rect):
                    obj.draw(self.screen, camera)

        # Dynamic Entities (Actors, Particles, etc. via Scene)
        self.scene.draw(self.screen, camera)

        if self.show_inventory:
            self.player.inventory.draw(self.screen)

    def load_map(self, file_path):
        """Parses the .tmx file and populates sprite groups based on layer names."""
        tmx_data = load_pygame(file_path)

        # Create a static surface for the floor to save draw calls
        map_width = tmx_data.width * TILESIZE
        map_height = tmx_data.height * TILESIZE
        self.map_surface = pygame.Surface((map_width, map_height)).convert()

        layer_names = [
            "Floor",
            "Walls",
            "Wall_Decor",
            "Floor_Decor",
            "Door_Tiles",
            "Items",
            "Chests",
        ]
        logic_layer = tmx_data.get_layer_by_name("Logic_Layer")

        for layer in tmx_data.visible_layers:
            if layer.name not in layer_names:
                continue

            if layer.name == "Floor":
                for x, y, surf in layer.tiles():
                    self.map_surface.blit(surf, (x * TILESIZE, y * TILESIZE))

            elif layer.name == "Walls":
                for x, y, surf in layer.tiles():
                    WallTile(
                        groups=self.wall_tiles,
                        image=surf,
                        pos=(x * TILESIZE, y * TILESIZE),
                    )

            elif layer.name in ["Wall_Decor", "Floor_Decor"]:
                for x, y, surf in layer.tiles():
                    DecorTile(
                        groups=self.sprites,
                        image=surf,
                        pos=(x * TILESIZE, y * TILESIZE),
                    )

            elif layer.name == "Door_Tiles":
                for x, y, surf in layer.tiles():
                    door_tile = Door(
                        groups=self.door_tiles,
                        image=surf,
                        pos=(x * TILESIZE, y * TILESIZE),
                    )
                    # Extract door_id property from the logic layer at the same coordinate
                    logic_props = tmx_data.get_tile_properties(
                        x, y, tmx_data.layers.index(logic_layer)
                    )
                    if logic_props:
                        door_tile.door_id = logic_props.get("door_id")

            elif layer.name == "Chests":
                for obj in layer:
                    if obj.name.lower() == "chest":
                        Chest(pos=(obj.x, obj.y), groups=self.chests, map=self)

    def unlock_door(self, door_id):
        for door in self.door_tiles.sprites():
            if door.door_id == door_id:
                door.kill()

        self.scene.set_wall_tiles(list(self.wall_tiles) + list(self.door_tiles))
