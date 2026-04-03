"""
System: Animation Component
---------------------------
Provides a bridge between an entity and its AnimationController.
This component handles the logic for switching between different
animation states and ensures the parent node's image is updated
to the current frame of the active sequence.

Classes:
    AnimationComponent: Manages the playback and switching of sprites.
"""

from Controllers.animations import AnimationController
from Components.component import Component
from typing import Any, Dict, List


class AnimationComponent(Component):
    def __init__(
        self,
        node: Any,
        animations: Dict[str, List[Any]],
        start_anim: str,
        anim_speed: float = 10.0,
    ) -> None:
        """
        Initializes the component and its internal controller.

        Args:
            node: Parent object that holds the image attribute.
            animations: A dictionary mapping animation names to lists of surfaces.
            start_anim: The key of the animation to play upon initialization.
            anim_speed: The default playback speed for the sequences.
        """
        super().__init__(node)
        self.anim_speed = anim_speed

        self.controller = AnimationController(
            animations=animations,
            start_anim=start_anim,
            animation_speed=self.anim_speed,
        )

    def change_anim(self, anim_name: str) -> None:
        """
        Updates the current active animation sequence.

        Args:
            anim_name: The dictionary key for the new animation.
        """
        self.controller.set_animation(anim_name)

    def update(self, dt: float) -> None:
        """
        Advances the animation frame based on time and updates the node image.

        Args:
            dt: Delta time for frame-independent playback.
        """
        self.node.image = self.controller.play_animation(dt, loop=True)
