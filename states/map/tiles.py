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

from globals import BLUE
from systems import debug
from systems.camera import camera
from systems.hitbox import draw_hitbox


class WallTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        """Initializes a solid wall with an attached Hitbox for collision."""
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)

    def draw(self, screen):
        """Renders the tile relative to the global camera position."""
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        if debug.show_hitboxes:
            draw_hitbox(screen, self.image, self.rect, camera, BLUE)


class DecorTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        """Initializes a decorative tile (grass, rugs, floor detail)."""
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)

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

    def draw(self, screen):
        """Renders the door relative to the global camera position."""
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
