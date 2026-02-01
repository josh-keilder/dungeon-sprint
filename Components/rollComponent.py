import pygame
from Components.component import Component

class RollComponent(Component):
    def __init__(self, node, roll_speed=1, cooldown=3000):
        super().__init__(node)
        # --- ATTRIBUTES ---
        self.is_rolling = False  # Initialize our roll check as false 
        self.roll_speed = roll_speed # how fast the roll moves
        self.is_invincible = False # Invincibility is initialized as false 
        self.last_roll_time = 0
        self.roll_cooldown = cooldown # in milliseconds
        self.roll_direction = pygame.Vector2(0,0)

        # --- VISUALS ---
        self.roll_anim = None

    def start_roll(self, dir_vector, last_direction):
        current_time = pygame.time.get_ticks()
        if not self.is_rolling and current_time - self.last_roll_time >= self.roll_cooldown:
            self.is_rolling = True
            self.is_invincible = True
            self.last_roll_time = current_time

            # --- MOMENTUM CAPTURE ---
            current_vel = self.node.movement.velocity.length()

            if dir_vector.length() == 0:
                self.roll_direction = pygame.Vector2(0,0) # Or a default vector
            else:
                self.roll_direction = dir_vector.normalize()


            self.current_roll_velocity = max(current_vel * 1.5, 300)

            # --- VISUALS ---
            self.roll_anim = f'{self.node.name}_roll_{last_direction}'
            if hasattr(self.node, 'animations'):
                self.node.animations.controller.set_animation(self.roll_anim)

    def update(self, dt):
        if self.is_rolling:
            wall_tiles = getattr(self.node, 'wall_tiles', [])
            move_x = self.roll_direction.x * self.roll_speed * dt
            move_y = self.roll_direction.y * self.roll_speed * dt

            self.node.rect.x += move_x
            if wall_tiles:
                for wall in wall_tiles:
                    if self.node.rect.colliderect(wall.rect):
                        self.node.rect.x -= move_x
                        break
            self.node.rect.y += move_y
            if wall_tiles:
                for wall in wall_tiles:
                    if self.node.rect.colliderect(wall.rect):
                        self.node.rect.y -= move_y
                        break

            if hasattr(self.node, 'animations'):
                self.node.image = self.node.animations.controller.play_animation(dt, loop=False)
                frames = self.node.animations.controller.animations[self.node.animations.controller.current_anim]

                # End roll when animation finishes
                if self.node.animations.controller.frame_index >= len(frames) - 1:
                    self.is_rolling = False
                    self.is_invincible = False