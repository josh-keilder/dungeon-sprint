"""
System: Base Component Class
---------------------------
Defines the blueprint for all entity behaviors. In a Component-Based
Architecture, this class allows for modular logic (like movement,
health, or input) to be attached to game objects.

Classes:
    Component: The abstract base for all modular game logic.
"""

from typing import Any, Optional
import pygame


class Component:
    def __init__(self, node: Any) -> None:
        """
        Initializes the component with a reference to its parent object.

        Args:
            node: The entity or game object this component belongs to.
        """
        self.node = node

    def update(self, dt: float = 0.0) -> None:
        """
        Handles logic updates per frame.

        Args:
            dt: Delta time representing the time passed since the last frame.
        """
        pass

    def draw(self, screen: pygame.Surface, camera: Optional[Any] = None) -> None:
        """
        Handles visual rendering for the component.

        Args:
            screen: The Pygame surface to render onto.
            camera: Optional camera object to offset drawing coordinates.
        """
        pass
