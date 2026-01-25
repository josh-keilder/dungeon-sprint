import pygame
from globals import *

from pytmx.util_pygame import load_pygame
from states.map.tiles import FloorTile, WallTile, ObjTile, Door, Key

from Entities.player.load_player import load_player
from ui_objects.camera import camera_update, camera
from ui_objects.create_outline import create_outline
from Entities.enemies.load_enemies import load_enemies
from states.scene import Scene

pygame.mixer.init()

class Dungeon_Level_One:
    def __init__(self, screen, gameStateManager, file_path = None):
        self.screen = screen
        self.gameStateManager = gameStateManager

        self.file_path = None

        # Create Scene
        self.scene = Scene()

        # Sprite Groups
        self.sprites = pygame.sprite.Group()
        self.wall_tiles = pygame.sprite.Group()
        self.door_tiles = pygame.sprite.Group()
        self.keys = pygame.sprite.Group()

        self.player_group = pygame.sprite.GroupSingle()
        self.enemies_group = pygame.sprite.Group()


        # Loads our map
        self.load_map(file_path = DUNGEON_LEVEL_ONE)

        # Loads our player
        self.player = load_player(map = self)
        self.scene.add_child(self.player)
        self.interact_cooldown = 0


        # Loads all of our enemies
        self.enemies = load_enemies(player=self.player)
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

        # Keeps the camera on the player       
        camera_update(self.player)

    def draw(self):
        # Draws our sprites and walls to the screen 
        for sprite in self.sprites:
            sprite.draw(self.screen)
        for wall in self.wall_tiles:
            wall.draw(self.screen)
        for door in self.door_tiles:
            door.draw(self.screen)
            if door.pos.distance_to(self.player.pos) < UNLOCK_DOOR_DIST:
                door.hitbox.draw(self.screen, camera=camera, color= WHITE, skip_debug = True)

        for key in self.keys:
            key.draw(self.screen)
            if key.pos.distance_to(self.player.pos) < PICK_UP_KEY_DIST:
                key.hitbox.draw(self.screen, camera=camera, color= BLACK, skip_debug = True)

        # Draw the scene
        self.scene.draw(self.screen, camera)

    def load_map(self, file_path):
        layer_names = [
            'Floor', 
            'Walls', 
            'Decor',
            'Door_Tiles',
            'Doors',
            'Keys'
            ]
        tmx_data = load_pygame(file_path)
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

                if layer.name == 'Decor':
                    for x, y, surf in layer.tiles():
                        pos = (x * TILESIZE, y * TILESIZE)
                        ObjTile(groups= self.sprites, image=surf, pos= pos)

                if layer.name == 'Door_Tiles':
                    for x, y, surf in layer.tiles():
                        pos = (x * TILESIZE, y * TILESIZE)
                        door_tile = Door(groups= self.door_tiles, image=surf, pos= pos)
                        for obj in tmx_data.objects:
                            if int(obj.x) == pos[0] and int(obj.y) == pos[1]:
                                door_tile.door_id = obj.properties.get('id', None)
                                break

                if layer.name == 'Keys':
                    for x, y, surf in layer.tiles():
                        pos = (x * TILESIZE, y * TILESIZE)
                        key_tile = Key(groups= self.keys, image=surf, pos= pos)
                        for obj in tmx_data.objects:
                            if int(obj.x) == pos[0] and int(obj.y) == pos[1]:
                                key_tile.key_id = obj.properties.get('id', None)
                                break

    def unlock_door(self, door_id):
        for door in list(self.door_tiles):
            if door.door_id == door_id:
                self.door_tiles.remove(door)
        self.scene.set_wall_tiles(list(self.wall_tiles.sprites()) + list(self.door_tiles.sprites()))