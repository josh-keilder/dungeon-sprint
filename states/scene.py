"""
Core System: Scene Management
-----------------------------
A specialized Node that acts as a container for game levels. It manages
high-level interactions between entities, such as player-enemy collisions
and wall tile distribution, while providing optimized access to key
gameplay objects.

Classes:
    Scene: Manages the lifecycle and interactions of entities within a level.
"""

from node import Node
from Entities.enemies.enemy import Enemy
import pygame
from systems.collision import find_player_contacts
from systems.combat import resolve_contact


class Scene(Node):
    def __init__(self):
        """Initializes the scene with categorized lists for optimized access."""
        super().__init__()
        self.active = True
        self.wall_tiles = []
        self.player = None
        self.enemies = []

    def set_wall_tiles(self, wall_tiles):
        """
        Assigns collision tiles to the scene and propagates them to all
        relevant child nodes (like players or NPCs).
        """
        self.wall_tiles = wall_tiles
        for child in self.children:
            if hasattr(child, "wall_tiles"):
                child.wall_tiles = wall_tiles

    def add_child(self, child):
        """
        Overrides Node.add_child to automatically categorize important
        entities for faster access during update loops.
        """
        super().add_child(child)

        if hasattr(child, "name") and child.name == "player":
            self.player = child
        elif isinstance(child, Enemy):
            self.enemies.append(child)

    def remove_child(self, child):
        """Safely removes a child and clears its reference from categorized lists."""
        super().remove_child(child)
        if child == self.player:
            self.player = None
        if child in self.enemies:
            self.enemies.remove(child)

    def update(self, dt=0):
        """
        Performs standard updates and runs collision detection logic
        between the player and enemies.
        """
        super().update(dt)

        if self.player is None:
            return

        contacts = find_player_contacts(self.player, self.enemies)

        for enemy in contacts:
            resolve_contact(self.player, enemy)

            if enemy.health.is_dead():
                self.remove_child(enemy)

    def draw(self, screen, camera=None):
        """Renders the scene using the base Node's Y-sorting logic."""
        super().draw(screen, camera)
