import pygame, random
from globals import *
from Components.component import Component

class MovementComponent(Component):
    def __init__(self, node, speed=100, behavior='basic', player=None):
        super().__init__(node)
        # --- ATTRIBUTES ---
        self.node = node
        self.max_speed = speed

        self.velocity = pygame.math.Vector2(0,0)
        self.acceleration = 2400
        self.friction = 3000
        self.speed_multiplier = 1.0

        self.flying = False
        self.behavior = behavior
        self.player = player
        self.flee_timer = 0
        self.return_timer = 0
        self.idle_direction = pygame.math.Vector2(random.choice([-1,1]), random.choice([-1, 1]))

    def update(self, dt=0):
        if self.behavior == 'fly' and self.player:
            self.fly_behavior(dt)
        elif self.behavior == 'wander_chase' and self.player:
            self.wander_chase_behavior(dt)
        else:
            if hasattr(self.node, 'input_vector'):
                target_dir = self.node.input_vector

                if target_dir.length() > 0:
                    if target_dir.length() > 1:
                        target_dir.normalize()
                    
                    if self.velocity.length() > 0 and target_dir.dot(self.velocity.normalize()) < -0.5:
                        self.velocity -= self.velocity * self.friction * 0.01 * dt

                    self.velocity += target_dir * self.acceleration * dt

                else:
                    if self.velocity.length() > 0:
                        drag_multiplier = 1.2
                        friction_vec = self.velocity.normalize() * (self.friction * drag_multiplier) * dt
                        if self.velocity.length() < friction_vec.length():
                            self.velocity = pygame.math.Vector2(0,0)
                        else:
                            self.velocity -= friction_vec

                current_limit = self.max_speed * self.speed_multiplier

                if self.velocity.length() > current_limit:
                    self.velocity.scale_to_length(current_limit)

                wall_tiles = getattr(self.node, 'wall_tiles', [])
                self.move(self.velocity * dt, wall_tiles)

    def fly_behavior(self, dt):
        distance = self.node.pos.distance_to(self.player.pos)
        # Fly around player, ignore walls
        if self.flee_timer > 0:
            self.flee_timer -= dt
            # Flee away from player
            dir_vector = (self.node.pos - self.player.pos).normalize() * self.speed
        elif self.return_timer > 0:
            self.return_timer -= dt
            # Return to player
            dir_vector = (self.player.pos - self.node.pos).normalize() * self.speed
        elif distance < 200: # Attack distance, fly to player
            dir_vector = (self.player.pos - self.node.pos).normalize() * self.speed
        else:
            # Idle wandering
            dir_vector = self.idle_direction * self.speed * 0.2  # Slower idle movement
            if random.random() < 0.01:  # Occasionally change direction
                self.idle_direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
    
        
        self.node.rect.x += dir_vector.x * dt
        self.node.rect.y += dir_vector.y * dt
        self.node.pos = pygame.math.Vector2(self.node.rect.topleft)

    def wander_chase_behavior(self, dt):
        if self.has_line_of_sight():  # Chase range
            # Chase player
            dir_vector = (self.player.pos - self.node.pos).normalize() * self.speed
        else:
            # Idle wander
            dir_vector = self.idle_direction * self.speed * 0.2  # Slower
            if random.random() < 0.01:  # Occasionally change direction
                self.idle_direction = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
        
        wall_tiles = getattr(self.node, 'wall_tiles', [])
        self.move(dir_vector * dt, wall_tiles)

    def trigger_flee(self):
        # Call this on attack (e.g., from health component)
        self.flee_timer = 2.0  # Flee for 2 seconds
        self.return_timer = 3.0  # Then return for 3 seconds

    def has_line_of_sight(self):
        if not self.player or not hasattr(self.node, 'wall_tiles'):
            return False
        start = self.node.pos
        end = self.player.pos
        # Check if any wall blocks the line
        for wall in self.node.wall_tiles:
            if wall.rect.clipline(start, end):  # Returns clipped line if intersects, else None
                return False
        return True
    
    def move(self, dir_vector, wall_tiles):
        self.node.rect.x += dir_vector.x 
        if wall_tiles and not self.flying:
            for wall in wall_tiles:
                if self.node.rect.colliderect(wall.rect):
                    if dir_vector.x > 0: self.node.rect.right = wall.rect.left
                    if dir_vector.x < 0: self.node.rect.left = wall.rect.right
                    self.velocity.x = 0
                    break
        self.node.rect.y += dir_vector.y 
        if wall_tiles and not self.flying:
            for wall in wall_tiles:
                if self.node.rect.colliderect(wall.rect):
                    if dir_vector.y > 0: self.node.rect.bottom = wall.rect.top
                    if dir_vector.y < 0: self.node.rect.top = wall.rect.bottom
                    self.velocity.y = 0
                    break
        
        self.node.pos = pygame.math.Vector2(self.node.rect.topleft)