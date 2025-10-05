import pygame
from settings import *
from texturedata import player_texture_data
from animations import Animations

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, animations, pos = (0,0)):
        super().__init__(groups)
        # Animation and image initialization
        self.animations = animations 
        self.player_animations = Animations(animations= self.animations, start_anim= 'player_idle_down')
        self.last_direction = 'down' # Tracking the last direction moved
        self.image = self.player_animations.play_animation(loop=True)

        # Player rect initialization
        self.rect = self.image.get_frect()
        self.rect.center = pos
        
        self.is_rolling = False  # Initialize our roll check as false 
        self.roll_speed = 2      # how fast the roll moves
        self.is_invincible = False # Invincibility is initialized as false 
        self.last_roll_time = 0
        self.roll_cooldown = 3000 # in milliseconds

    def input(self, wall_tiles):
        keys = pygame.key.get_pressed()
        walking = False
        player_speed = 1
        dir_x, dir_y = 0 , 0

        # Checks to see if we are rolling, if we are, no other movement is possible
        if self.is_rolling:
            return 
        # Move left
        if keys[pygame.K_a]:
            self.last_direction = 'left'
            self.player_animations.set_animation('player_walk_left')
            walking = True
            dir_x -= player_speed
        # Move right
        if keys[pygame.K_d]:
            self.last_direction = 'right'
            self.player_animations.set_animation('player_walk_right')
            walking = True          
            dir_x += player_speed
        # Move up
        if keys[pygame.K_w]:
            walking = True
            self.last_direction = 'up'
            self.player_animations.set_animation('player_walk_up')
            dir_y -= player_speed

        # Move down
        if keys[pygame.K_s]:
            self.last_direction = 'down'
            self.player_animations.set_animation('player_walk_down')
            walking = True    
            dir_y += player_speed
        
        # Sets the correct idle based on last direction walked
        if not walking:
            self.player_animations.set_animation(f'player_idle_{self.last_direction}')

        # If we aren't already rolling, and we press SPACE, we will roll and we set the cooldown to be 3 seconds between rolls
        current_time = pygame.time.get_ticks()
        if not self.is_rolling and keys[pygame.K_SPACE] and walking and current_time - self.last_roll_time >= self.roll_cooldown:
            self.roll()
            self.roll_direction = (dir_x, dir_y)
            self.last_roll_time = current_time
            
        # Normalizes our speed so when we move diagonally its the same as if we move vertically or horizontally separately
        input_vector = pygame.math.Vector2(dir_x, dir_y)
        if input_vector.length() > 0:
            input_vector = input_vector.normalize()
        # Collision check and movement call
        self.move(input_vector.x * player_speed, input_vector.y * player_speed, wall_tiles)

    def move(self, dir_x, dir_y, wall_tiles):
        self.rect.x += dir_x
        if pygame.sprite.spritecollide(self, wall_tiles, dokill=False, collided=None):
            self.rect.x -= dir_x

        self.rect.y += dir_y
        if pygame.sprite.spritecollide(self, wall_tiles, dokill=False, collided=None):
            self.rect.y -= dir_y


    def roll(self):
        self.is_rolling = True
        self.is_invincible = True
        # pick roll direction based on last direction
        if self.last_direction == 'left':
            self.player_animations.set_animation('player_roll_left')
        elif self.last_direction == 'right':
            self.player_animations.set_animation('player_roll_right')
        elif self.last_direction == 'up':
            self.player_animations.set_animation('player_roll_up')
        elif self.last_direction == 'down':
            self.player_animations.set_animation('player_roll_down')

    def update(self, wall_tiles):

        if self.is_rolling: # Checks if the player is rolling and since it isn't a looping animation we play it separately
            dir_x, dir_y = self.roll_direction
            self.move(dir_x * self.roll_speed, dir_y * self.roll_speed, wall_tiles)
            self.image = self.player_animations.play_animation(loop=False)

            frames = self.player_animations.animations[self.player_animations.current_anim]
            if self.player_animations.frame_index >= len(frames) - 1:
                self.is_rolling = False
                self.is_invincible = False
        else:
            self.input(wall_tiles) # Checks for inputs and passes the wall tiles through to check for collisions
            self.image = self.player_animations.play_animation(loop=True)
            
    def gen_player_textures(self) -> dict:
        textures = {}

        for name, data in player_texture_data.items():
            player_img = pygame.image.load(data['file_path']).convert_alpha()
            w, h = data['size'] # unpacks the size tuple
            frames = data['frames']
            row = data['position'][1]
            textures[name] = []

            for i in range(frames):
                x = i * w
                y = row * h
                frame = player_img.subsurface(pygame.Rect(x, y, w, h))

                # Since the player sprites are 64x64, you have to crop out just the center player to get the hitbox to be the right size
                center_x = (w - 16) // 2
                center_y = (h - 16) // 2
                center_rect = pygame.Rect(center_x, center_y, 16, 16)
                cropped_frame = frame.subsurface(center_rect).copy()

                textures[name].append(cropped_frame)
        return textures