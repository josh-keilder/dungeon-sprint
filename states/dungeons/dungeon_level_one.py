import pygame
from globals import *

from Entities.player.load_player import load_player
from states.dungeons.map_loader import load_map
from ui_objects.camera import camera_update
from Entities.enemies.load_enemies import load_enemies
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

        # Loads our map
        self.map = load_map(self.sprites, self.wall_tiles, file_path = DUNGEON_LEVEL_ONE)
        # Loads our player
        self.player = load_player(self.player_group)
        # Loads all of our enemies
        self.enemies = load_enemies(self.enemies_group)
        

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
        
        # Taking damage test
        for enemy in self.enemies:
            if enemy.hitbox.collides_with(self.player.hitbox):
                self.player.health.take_damage(enemy.attack_damage )
                enemy.health.take_damage(1)
            else:
                self.player.health.take_damage(0)
                enemy.health.take_damage(0)

        print(self.player.health.current)

        # Keeps the camera on the player       
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