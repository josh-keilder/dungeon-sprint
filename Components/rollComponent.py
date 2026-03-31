import pygame
from Components.component import Component


class RollComponent(Component):
    def __init__(self, node, roll_speed=0, cooldown=800):
        super().__init__(node)
        # --- ATTRIBUTES ---
        self.is_rolling = False
        self.roll_speed = roll_speed
        self.is_invincible = False
        self.last_roll_time = 0
        self.roll_cooldown = cooldown
        self.roll_direction = pygame.Vector2(0, 0)

    def start_roll(self, dir_vector, last_direction):
        current_time = pygame.time.get_ticks()
        if (
            not self.is_rolling
            and current_time - self.last_roll_time >= self.roll_cooldown
        ):
            self.is_rolling = True
            self.is_invincible = True
            self.last_roll_time = current_time

            # Capture direction or use default based on facing
            if dir_vector.length_squared() == 0:
                dir_map = {
                    "right": (1, 0),
                    "left": (-1, 0),
                    "up": (0, -1),
                    "down": (0, 1),
                }
                self.roll_direction = pygame.Vector2(
                    dir_map.get(last_direction, (1, 0))
                )
            else:
                self.roll_direction = dir_vector.normalize()

            if hasattr(self.node, "animations"):
                self.node.animations.change_anim(f"player_roll_{last_direction}")

    def update(self, dt):
        if self.is_rolling:
            # Use shared movement logic for consistent wall collisions
            if hasattr(self.node, "movement"):
                vel = self.roll_direction * self.roll_speed
                self.node.movement.move(vel * dt, getattr(self.node, "wall_tiles", []))

            # Handle animation frames and early exit buffer
            if hasattr(self.node, "animations"):
                controller = self.node.animations.controller
                frames = controller.animations.get(controller.current_anim, [])

                # Allow movement keys to break the roll near the end of the animation
                progress = controller.frame_index / max(1, len(frames) - 1)
                if progress > 0.8:
                    input_vec = getattr(self.node, "input_vector", pygame.Vector2(0, 0))
                    if input_vec.length_squared() > 0:
                        self.finish_roll()

                # End roll on last frame
                if controller.frame_index >= len(frames) - 1:
                    self.finish_roll()

    def finish_roll(self):
        self.is_rolling = False
        self.is_invincible = False
