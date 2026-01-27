import pygame, random
from globals import *

from pytmx.util_pygame import load_pygame
from states.map.tiles import FloorTile, WallTile, DecorTile, Door

from Entities.player.load_player import load_player
from ui_objects.camera import camera_update, camera
from ui_objects.create_outline import create_outline
from Entities.enemies.load_enemies import load_enemies
from states.scene import Scene

from items.items import Chest, WorldItem
from items.itemDataBase import initialize_item_database

pygame.mixer.init()

class Dungeon_Level_One:
    def __init__(self, screen, gameStateManager, file_path = None):
        self.screen = screen
        self.gameStateManager = gameStateManager

        self.file_path = DUNGEON_LEVEL_ONE

        # Create Scene
        self.scene = Scene()

        # Sprite Groups
        self.sprites = pygame.sprite.Group()
        self.wall_tiles = pygame.sprite.Group()
        self.door_tiles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.chests = pygame.sprite.Group()

        self.player_group = pygame.sprite.GroupSingle()
        self.enemies_group = pygame.sprite.Group()

        # Loads our items
        self.ITEM_DATABASE = initialize_item_database()
        

        # Loads our map
        self.load_map(file_path = self.file_path)

        # Loads our player
        self.player = load_player(map = self)
        self.scene.add_child(self.player)
        self.interact_cooldown = 0


        # Loads all of our enemies
        self.enemies = load_enemies(player=self.player, file_path=self.file_path)
        for enemy in self.enemies:
            self.scene.add_child(enemy)
        
        # Set wall tiles in scene
        self.scene.set_wall_tiles(list(self.wall_tiles) + list(self.door_tiles))

        # Load the pause sound
        try:
            self.pause_sound = pygame.mixer.Sound("Assets/Sounds/Pause.wav")
        except Exception:
            self.pause_sound = None

    def update(self, dt):
        # Update the scene
        self.scene.update(dt)

        self.items.update(dt)

        # Keeps the camera on the player       
        camera_update(self.player)

    def draw(self):
        # Draws our sprites, tiles and objects to the screen 
        for sprite in self.sprites:
            sprite.draw(self.screen)
        for wall in self.wall_tiles:
            wall.draw(self.screen)
        for door in self.door_tiles:
            door.draw(self.screen)
            if door.pos.distance_to(self.player.pos) < UNLOCK_DOOR_DIST:
                door.hitbox.draw(self.screen, camera=camera, color= WHITE, skip_debug = True)

        for item in self.items:
            item.draw(self.screen, camera)

        for chest in self.chests:
            chest.draw(self.screen, camera)
            # if chest.pos.distance_to(self.player.pos) < OPEN_CHEST_DIST:
            #     chest.hitbox.draw(self.screen, camera=camera, color= WHITE, skip_debug = True)

        # Draw the scene
        self.scene.draw(self.screen, camera)

    def load_map(self, file_path):
        tmx_data = load_pygame(file_path)

        layer_names = [
            'Floor', 
            'Walls', 
            'Wall_Decor',
            'Floor_Decor',
            'Door_Tiles',
            'Items',
            'Chests'
            ]
        
        logic_layer = tmx_data.get_layer_by_name('Logic_Layer')
        
        for layer in tmx_data.visible_layers:
            if layer.name in layer_names: 
                if layer.name == 'Walls':
                    for x, y, surf in layer.tiles():
                        pos = (x * TILESIZE, y * TILESIZE)
                        WallTile(groups= self.wall_tiles, image=surf, pos= pos)

                if layer.name == 'Floor':
                    for x, y, surf in layer.tiles():
                        pos = (x * TILESIZE, y * TILESIZE)
                        FloorTile(groups= self.sprites, image=surf, pos= pos)

                if layer.name == 'Wall_Decor' or layer.name == 'Floor_Decor':
                    for x, y, surf in layer.tiles():
                        pos = (x * TILESIZE, y * TILESIZE)
                        DecorTile(groups= self.sprites, image=surf, pos= pos)

                if layer.name == 'Door_Tiles':
                    for x, y, surf in layer.tiles():
                        pos = (x * TILESIZE, y * TILESIZE)
                        door_tile = Door(groups= self.door_tiles, image=surf, pos= pos)
                        logic_props = tmx_data.get_tile_properties(x,y, tmx_data.layers.index(logic_layer))
                        if logic_props:
                            door_tile.door_id = logic_props.get('door_id')

                # For testing items
                # if layer.name == 'Items':
                #     for obj in layer:
                #         item_name = obj.name.lower()
                #         if item_name in ITEM_DATABASE:
                #             item_data = ITEM_DATABASE[item_name]
                #             WorldItem(pos=(obj.x, obj.y), groups = self.items, item_data = item_data)

                # Items will spawn from chests
                if layer.name == 'Chests':
                    for obj in layer:
                        if obj.name.lower() == 'chest':
                            Chest(pos=(obj.x, obj.y), groups=self.chests, map=self)