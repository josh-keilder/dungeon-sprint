"""
System: Hitbox and Collision Detection
--------------------------------------
An advanced collision component that utilizes pixel-perfect masks.
It features a global MASK_CACHE to prevent the expensive overhead of
re-generating bitmasks for identical surfaces (e.g., multiple enemies
using the same sprite).

Classes:
    Hitbox: Manages spatial rects and bitmasks for precise collision checks.
"""

import pygame
import globals
from globals import *
from ui_objects.camera import camera
from Components.component import Component
from typing import Any, Dict, Optional, Tuple

# Global cache to store pygame.mask.Mask objects keyed by their source Surface
MASK_CACHE: Dict[pygame.Surface, pygame.mask.Mask] = {}


class Hitbox(Component):
    def __init__(self, node: Any) -> None:
        """Initializes the hitbox with a copy of the node's rect and a bitmask."""
        super().__init__(node)
        self.rect = node.rect.copy()
        self.mask = self._get_cached_mask(node.image)

    def _get_cached_mask(self, surface: pygame.Surface) -> pygame.mask.Mask:
        """
        Retrieves a mask from the cache or creates a new one if it doesn't exist.
        Using the Surface object as a key provides O(1) lookup speed.
        """
        if surface not in MASK_CACHE:
            MASK_CACHE[surface] = pygame.mask.from_surface(surface)
        return MASK_CACHE[surface]

    def update(self, dt: float = 0.0) -> None:
        """Syncs the hitbox position with the parent node and updates the active mask."""
        # Update spatial position
        self.rect.topleft = self.node.rect.topleft

        # Ensure the mask matches the current animation frame/image
        self.mask = self._get_cached_mask(self.node.image)

    def collides_with(self, other_hitbox: "Hitbox") -> bool:
        """
        Performs a pixel-perfect overlap check between two hitboxes
        using an offset calculated from their relative screen positions.
        """
        offset = (other_hitbox.rect.x - self.rect.x, other_hitbox.rect.y - self.rect.y)
        return self.mask.overlap(other_hitbox.mask, offset) is not None

    def draw(
        self,
        screen: pygame.Surface,
        camera: Optional[Any] = None,
        color: Tuple[int, int, int] = RED,
        skip_debug: bool = False,
    ) -> None:
        """
        Visualizes the pixel-perfect outline of the mask.
        Only renders if global debug hitboxes are enabled or explicitly requested.
        """
        if globals.DEBUG_HITBOXES or skip_debug:
            # Adjust drawing position based on camera offset
            offset_x = self.rect.x - (camera.x if camera else 0)
            offset_y = self.rect.y - (camera.y if camera else 0)

            # Generate and draw the mask outline points
            outline = self.mask.outline()
            for p in outline:
                screen.set_at((int(offset_x + p[0]), int(offset_y + p[1])), color)
