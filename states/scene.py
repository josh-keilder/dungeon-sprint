from node import Node
from Entities.enemies.enemy import Enemy

class Scene(Node):
    def __init__(self):
        super().__init__()
        self.active = True
        self.wall_tiles = []

    def set_wall_tiles(self, wall_tiles):
        self.wall_tiles = wall_tiles
        # Set wall_tiles on all nodes that need it
        for child in self.children:
            if hasattr(child, 'wall_tiles'):
                child.wall_tiles = wall_tiles

    def update(self, dt=0):
        super().update(dt)
        # Handle collisions between player and enemies
        player = None
        enemies = []
        for child in self.children:
            if hasattr(child, 'name') and child.name == 'player':
                player = child
            elif isinstance(child, Enemy):
                enemies.append(child)

        if player:
            for enemy in enemies:
                if player.hitbox.collides_with(enemy.hitbox):
                    player.health.take_damage(enemy.attack_damage)
                    enemy.health.take_damage(1)
                    enemy.movement_component.trigger_flee()



                if enemy.health.current == 0:
                    self.remove_child(enemy)

    def draw(self, screen, camera=None):
        super().draw(screen, camera)