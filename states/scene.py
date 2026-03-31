from node import Node
from Entities.enemies.enemy import Enemy
import pygame

class Scene(Node):
    def __init__(self):
        super().__init__()
        self.active = True
        self.wall_tiles = []
        # Pre-categorize for speed
        self.player = None
        self.enemies = []

    def set_wall_tiles(self, wall_tiles):
        self.wall_tiles = wall_tiles
        # Set wall_tiles on all nodes that need it
        for child in self.children:
            if hasattr(child, 'wall_tiles'):
                child.wall_tiles = wall_tiles

    def add_child(self, child):
        super().add_child(child)
        # Sort them as they come in, not every frame
        if hasattr(child, 'name') and child.name == 'player':
            self.player = child
        elif isinstance(child, Enemy):
            self.enemies.append(child)

    def remove_child(self, child):
        super().remove_child(child)
        if child == self.player:
            self.player = None
        if child in self.enemies:
            self.enemies.remove(child)

    def update(self, dt=0):
        super().update(dt)
        
        if self.player:
            for enemy in self.enemies:
                if self.player.pos.distance_to(enemy.pos) < 100:
                    if self.player.hitbox.collides_with(enemy.hitbox):
                        self.handle_collision(self.player, enemy)

    def handle_collision(self, player, enemy):
        player.health.take_damage(enemy.attack_damage)
        enemy.health.take_damage(1)
        enemy.movement_component.trigger_flee()

        if enemy.health.current <= 0:
            self.remove_child(enemy)

    def draw(self, screen, camera=None):
        super().draw(screen, camera)