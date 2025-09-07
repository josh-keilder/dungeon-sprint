import pygame
from settings import *
from texturedata import player_texture_data

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, animations, start_anim = 'player_idle_down', pos = (0,0)):
        super().__init__(groups)
        # Animation initialization
        self.animations = animations 
        self.current_anim = start_anim
        self.frame_index = 0
        self.animation_speed = 0.15 # Speed of animation, we have 6 frames per animation for 1 second equals 0.15
        self.frame_timer = 0
        self.last_direction = 'down' # Tracking the last direction moved
        self.image = self.animations[self.current_anim][self.frame_index]

        # Player rect initialization
        self.rect = self.image.get_rect()
        self.rect.center = pos
        
        self.is_rolling = False  # Initialize our roll check as false 
        self.roll_speed = 2      # how fast the roll moves
        self.is_invincible = False # Invincibility is initialized as false 
        self.last_roll_time = 0
        self.roll_cooldown = 3000 # in milliseconds

    def set_animation(self, anim_name, loop = True):
        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.frame_index = 0
            self.image = self.animations[self.current_anim][self.frame_index]
            self.loop = loop

    def play_animation(self, loop = False):
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index += 1

            # Handle flipped animations
            if self.current_anim.endswith("_left"):
                right_key = self.current_anim.replace("left", "right")
                right_frames = self.animations[right_key]
                frames = [pygame.transform.flip(f, True, False) for f in right_frames]
            else:
                frames = self.animations[self.current_anim]

            if loop: # Looping animations (idle/walk)
                self.frame_index %= len(frames)
                self.image = frames[self.frame_index]
            else: # Non-looping animations (rolling)
                if self.frame_index >= len(frames):
                    self.is_rolling = False
                    self.is_invincible = False
                else:
                    self.image = frames[self.frame_index]


    def move(self, dir_x, dir_y, wall_tiles):
        self.rect.x += dir_x
        if pygame.sprite.spritecollide(self, wall_tiles, dokill=False, collided=None):
            self.rect.x -= dir_x

        self.rect.y += dir_y
        if pygame.sprite.spritecollide(self, wall_tiles, dokill=False, collided=None):
            self.rect.y -= dir_y


    def input(self, wall_tiles):
        keys = pygame.key.get_pressed()
        walking = False
        running = False
        stamina = 100
        player_speed = 1
        dir_x = 0
        dir_y = 0

        # Checks to see if we are rolling, if we are, no other movement is possible
        if self.is_rolling:
            return 
        # Move left
        if keys[pygame.K_a]:
            self.last_direction = 'left'
            self.set_animation('player_walk_left')
            walking = True
            # Run
            if keys[pygame.K_LSHIFT] and walking and not self.is_rolling:
                player_speed = 2
                running = True
                if running:
                    self.animation_speed = 0.25
            else:
                self.animation_speed = 0.15    
                running = False
            dir_x -= player_speed
        # Move right
        if keys[pygame.K_d]:
            self.last_direction = 'right'
            self.set_animation('player_walk_right')
            walking = True
            # Run
            if keys[pygame.K_LSHIFT] and walking and not self.is_rolling:
                player_speed = 2
                running = True
                if running:
                    self.animation_speed = 0.25
            else:
                self.animation_speed = 0.15    
                running = False            
            dir_x += player_speed
        # Move up
        if keys[pygame.K_w]:
            walking = True
            self.last_direction = 'up'
            self.set_animation('player_walk_up')
            # Run
            if keys[pygame.K_LSHIFT] and walking and not self.is_rolling:
                player_speed = 2
                running = True
                if running:
                    self.animation_speed = 0.25
            else:
                self.animation_speed = 0.15    
                running = False
            dir_y -= player_speed

        # Move down
        if keys[pygame.K_s]:
            self.last_direction = 'down'
            self.set_animation('player_walk_down')
            walking = True
            # Run
            if keys[pygame.K_LSHIFT] and walking and not self.is_rolling:
                player_speed = 2
                running = True
                if running:
                    self.animation_speed = 0.25
            else:
                self.animation_speed = 0.15    
                running = False     
            dir_y += player_speed
        
        # Sets the correct idle based on last direction walked
        if not walking:
            self.set_animation(f'player_idle_{self.last_direction}')

        # If we aren't already rolling, and we press SPACE, we will roll and we set the cooldown to be 3 seconds between rolls
        current_time = pygame.time.get_ticks()
        if not self.is_rolling and keys[pygame.K_SPACE] and walking and current_time - self.last_roll_time >= self.roll_cooldown:
            self.is_rolling = True
            self.is_invincible = True
            self.frame_index = 0
            self.frame_timer = 0
            self.animation_speed = 0.2

            # pick roll direction based on last direction and assign our dir_x and dir_y variables as the direction
            self.roll_direction = (dir_x, dir_y)
            if self.last_direction == 'left':
                self.set_animation('player_roll_left')
            elif self.last_direction == 'right':
                self.set_animation('player_roll_right')
            elif self.last_direction == 'up':
                self.set_animation('player_roll_up')
            elif self.last_direction == 'down':
                self.set_animation('player_roll_down')

            self.last_roll_time = current_time
        # Collision check and movement
        self.move(dir_x, dir_y, wall_tiles)

    def update(self, wall_tiles):
        if self.is_rolling: # Checks if the player is rolling and since it isn't a looping animation we play it separately
            dir_x, dir_y = self.roll_direction
            self.move(dir_x * self.roll_speed, dir_y * self.roll_speed, wall_tiles)
            self.play_animation(loop=False)
        else:
            self.input(wall_tiles) # Checks for inputs and passes the wall tiles through to check for collisions
            self.play_animation(loop=True)
            
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