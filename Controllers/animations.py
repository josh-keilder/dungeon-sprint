"""
System: Animation Controller
----------------------------
Manages the playback and switching of sprite-based animations. It handles
frame timing, looping logic, and provides a utility for dynamic sprite
flipping to generate directional variants on the fly.

Classes:
    AnimationController: Tracks frame indices and timers for a set of animations.
"""

import pygame
from globals import *
from typing import Dict, List, Any


class AnimationController:
    def __init__(
        self,
        animations: Dict[str, List[pygame.Surface]],
        start_anim: str,
        animation_speed: float,
    ) -> None:
        """Initializes the controller with animation data and playback settings."""
        self.animations = animations
        self.current_anim = start_anim
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.frame_timer = 0

    def set_animation(self, anim_name: str) -> None:
        """
        Switches the active animation state. If a left-facing variant is missing,
        it generates one by flipping the corresponding right-facing animation.
        """
        if anim_name != self.current_anim:
            # Dynamic asset generation for mirrored animations
            if anim_name not in self.animations and anim_name.endswith("_left"):
                right_key = anim_name.replace("_left", "_right")
                if right_key in self.animations:
                    self.animations[anim_name] = [
                        pygame.transform.flip(f, True, False)
                        for f in self.animations[right_key]
                    ]

            if anim_name in self.animations:
                self.current_anim = anim_name
                self.frame_index = 0
                self.frame_timer = 0

    def play_animation(self, dt: float, loop: bool = True) -> pygame.Surface:
        """
        Increments the frame timer based on delta time and returns the current
        surface frame.
        """
        self.frame_timer += self.animation_speed * dt

        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index += 1

        frames = self.animations.get(self.current_anim)

        # Fallback to the first available animation if the current one is missing
        if not frames:
            frames = list(self.animations.values())[0]

        if loop:
            self.frame_index %= len(frames)
        else:
            self.frame_index = min(self.frame_index, len(frames) - 1)

        return frames[self.frame_index]
