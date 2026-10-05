from Components.component import Component
from typing import Any, Dict, List
import pygame


class AnimationComponent(Component):
    def __init__(
        self,
        node: Any,
        animations: Dict[str, List[Any]],
        start_animation: str,
        animation_speed: float = 10.0,
    ) -> None:
        super().__init__(node)
        self.animations = animations
        self.current_anim = start_animation
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.frame_timer = 0

    def set_animation(self, anim_name: str) -> None:
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
        self.frame_timer += self.animation_speed * dt

        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index += 1

        frames = self.animations.get(self.current_anim)

        if not frames:
            frames = list(self.animations.values())[0]

        if loop:
            self.frame_index %= len(frames)
        else:
            self.frame_index = min(self.frame_index, len(frames) - 1)

        return frames[self.frame_index]
    

    def update(self, dt: float) -> None:
        self.node.image = self.play_animation(dt, loop=True)
