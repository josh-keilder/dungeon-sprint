import pygame
from settings import *
from sprites import Entity
from texturedata import player_texture_data

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, animations, start_anim = 'player_idle_down', pos = (0,0)):
        super().__init__(groups)
        self.animations = animations 
        self.current_anim = start_anim
        self.frame_index = 0
        self.image = self.animations[self.current_anim][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.animation_speed = 0.15 # Speed of animation, we have 6 frames per animation for 1 second equals 0.15
        self.frame_timer = 0
        self.last_direction = 'down' # Tracking the last direction moved
    
    def set_animation(self, anim_name):
        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.frame_index = 0
            self.image = self.animations[self.current_anim][self.frame_index]
        
    def input(self):
        keys = pygame.key.get_pressed()
        walking = False
        running = False
        stamina = 100
        player_speed = 1

        # Move left
        if keys[pygame.K_a]:
            self.last_direction = 'left'
            self.set_animation('player_walk_left')
            walking = True
            # Run
            if keys[pygame.K_LSHIFT] and walking:
                player_speed = 2
                running = True
                if running:
                    self.animation_speed = 0.25
            else:
                self.animation_speed = 0.15    
                running = False
            self.rect.x -= player_speed
        # Move right
        if keys[pygame.K_d]:
            self.last_direction = 'right'
            self.set_animation('player_walk_right')
            walking = True
                    # Run
            if keys[pygame.K_LSHIFT] and walking:
                player_speed = 2
                running = True
                if running:
                    self.animation_speed = 0.25
            else:
                self.animation_speed = 0.15    
                running = False            
            self.rect.x += player_speed
        # Move up
        if keys[pygame.K_w]:
            walking = True
            self.last_direction = 'up'
            self.set_animation('player_walk_up')
            # Run
            if keys[pygame.K_LSHIFT] and walking:
                player_speed = 2
                running = True
                if running:
                    self.animation_speed = 0.25
            else:
                self.animation_speed = 0.15    
                running = False
            self.rect.y -= player_speed

        # Move down
        if keys[pygame.K_s]:
            self.last_direction = 'down'
            self.set_animation('player_walk_down')
            walking = True
            # Run
            if keys[pygame.K_LSHIFT] and walking:
                player_speed = 2
                running = True
                if running:
                    self.animation_speed = 0.25
            else:
                self.animation_speed = 0.15    
                running = False     
            self.rect.y += player_speed       
        
        #Sets the correct idle
        if not walking:
            self.set_animation(f'player_idle_{self.last_direction}')
    def update(self):
        # Checks for inputs
        self.input()

        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_anim])

            # Since there is no built in left facing animations, we take the right facing animations and flip them, otherwise set as normal animations
            if self.current_anim == 'player_walk_left':
                right_frames = self.animations['player_walk_right']
                self.image = pygame.transform.flip(right_frames[self.frame_index], True, False)
            elif self.current_anim == 'player_idle_left':
                right_frames = self.animations['player_idle_right']
                self.image = pygame.transform.flip(right_frames[self.frame_index], True, False)
            else:
                self.image = self.animations[self.current_anim][self.frame_index]           

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
                textures[name].append(frame)
        return textures