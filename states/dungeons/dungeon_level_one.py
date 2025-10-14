import pygame
from globals import *

from Characters.player.player import Player
from states.dungeons.map_loader import MapLoader
from states.dungeons.camera import camera_start, camera_update
from Characters.enemies.enemy import Enemy
from ui_objects.button import Button
from ui_objects.create_outline import create_outline

pygame.mixer.init()

# Dungeon Level One screen
class Dungeon_Level_One:
    def __init__(self, screen, gameStateManager, cursor):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.cursor = cursor

        # Sprite Groups
        self.sprites = pygame.sprite.Group()
        self.wall_tiles = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.enemies_group = pygame.sprite.Group()

        # Loads our tmx map file
        self.tilemap_dungeon = MapLoader.load_map(self, self.sprites, self.wall_tiles, file_path = DUNGEON_LEVEL_ONE)

        # Loads and creates the player and makes sure our camera starts with the player in the center
        self.player_textures = Player.gen_player_textures(self)
        self.player_pos = MapLoader.get_player_pos(self, file_path = DUNGEON_LEVEL_ONE)
        self.player = Player([self.player_group], animations=self.player_textures, pos = self.player_pos)
        camera_start(self.player.rect.center)
        
        # Spawns in enemies at enemy locations on the map
        self.enemies = []
        self.enemy_positions = MapLoader.get_enemy_pos(self, file_path = DUNGEON_LEVEL_ONE)
        print(self.enemy_positions)
        for pos in self.enemy_positions:
            new_enemy = Enemy(self.enemies_group, pos=pos)
            self.enemies.append(new_enemy)

        # Load the pause sound
        try:
            self.pause_sound = pygame.mixer.Sound("Assets/Sounds/Pause.wav")
        except Exception:
            self.pause_sound = None

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.gameStateManager.set_state('options')
            self.pause_sound.play()

        # Updates all sprites (Entities and player)
        self.player.update(self.wall_tiles) # Passes the wall tiles into the player and enemy group updates to test for collisions
        self.enemies_group.update(self.wall_tiles)
        self.sprites.update()
        self.wall_tiles.update()
        

        camera_update(self.player)

    def draw(self):
        # Draws our sprites and walls to the screen 
        for sprite in self.sprites:
            sprite.draw(self.screen)
        for wall in self.wall_tiles:
            wall.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.player_group.sprite:
           self.player_group.sprite.draw(self.screen)

        # Shows the wall hitboxes and player hitboxes for collision detection
        # for wall in self.wall_tiles:
        #     pygame.draw.rect(self.display, (255,0,0), wall.rect, 2)
        # pygame.draw.rect(self.display, (0,255,0), self.player.rect, 2)