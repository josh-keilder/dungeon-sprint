"""
System: Tile and Interactive Objects
------------------------------------
Defines the sprite-based components used to construct game levels.
Includes static physical barriers (WallTile), non-collidable visual
elements (DecorTile), and interactive transition points (Door).

Classes:
    WallTile: A collidable sprite representing world geometry.
    DecorTile: A background sprite with no collision logic.
    Door: An interactive sprite used for level transitions.
"""

import pygame
import random
from globals import *
from ui_objects.camera import camera
from Components.hitboxComponent import Hitbox


class WallTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        """Initializes a solid wall with an attached Hitbox for collision."""
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox = Hitbox(self)

    def update(self, dt):
        """Syncs the hitbox position with the tile position."""
        self.hitbox.update()

    def draw(self, screen):
        """Renders the tile relative to the global camera position."""
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        # Debug: Draws the collision boundary
        self.hitbox.draw(screen, camera=camera, color=BLUE)


class DecorTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        """Initializes a decorative tile (grass, rugs, floor detail)."""
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)

    def update(self, dt):
        """Static tiles usually require no logic updates."""
        pass

    def draw(self, screen):
        """Renders the decoration relative to the global camera position."""
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))


class Door(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        """Initializes a door tile with a unique ID for level linking."""
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)
        self.pos = pygame.math.Vector2(pos)
        self.door_id = None
        self.hitbox = Hitbox(self)

    def update(self, dt):
        """Syncs the hitbox for interaction/collision detection."""
        self.hitbox.update()

    def draw(self, screen):
        """Renders the door relative to the global camera position."""
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
