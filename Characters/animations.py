import pygame
from globals import *

class Animations:
    def __init__(self, animations, start_anim, animation_speed = 0.15):
        self.animations = animations 
        self.current_anim = start_anim
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.frame_timer = 0
    def set_animation(self, anim_name):
        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.frame_index = 0
            

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

            if loop:
                self.frame_index %= len(frames)
            else:
                if self.frame_index >= len(frames):
                    self.frame_index = len(frames) - 1
        frames = [pygame.transform.flip(f, True, False) for f in self.animations[self.current_anim]] if self.current_anim.endswith("_left") else self.animations[self.current_anim]
        return frames[self.frame_index]