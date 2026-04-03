"""
System: Health and Vitality UI
-----------------------------
Provides a logic-based Health component for tracking hit points and a visual
HealthBar component for rendering health status. The HealthBar supports
both static screen-space positions (for Player UI) and world-space positions
pinned to entities (for Enemies), with dynamic color shifting based on health.

Classes:
    Health: Manages numerical HP values, damage, and healing.
    HealthBar: Handles the graphical representation of a Health component.
"""

import pygame
from globals import *
from Components.component import Component
from typing import Any, Optional, Tuple


class Health(Component):
    def __init__(self, node: Any, max_health: float) -> None:
        """Initializes the entity's HP pool."""
        super().__init__(node)
        self.max_health = max_health
        self.current = max_health

    def take_damage(self, amount: float) -> None:
        """Reduces current HP, clamping at 0."""
        self.current = max(0.0, self.current - amount)

    def heal(self, amount: float) -> None:
        """Increases current HP, clamping at max_health."""
        self.current = min(self.max_health, self.current + amount)

    def is_dead(self) -> bool:
        """Returns True if HP has reached zero."""
        return self.current <= 0


class HealthBar(Component):
    def __init__(
        self,
        node: Any,
        max_health: float,
        width: int = TILESIZE,
        height: int = 4,
        shrink_speed: float = 10000.0,
        is_player: bool = False,
        pos: Tuple[int, int] = (20, 20),
    ) -> None:
        """
        Initializes visual parameters for the health bar.

        Args:
            node: Parent entity.
            max_health: The maximum HP value to scale against.
            width/height: Dimensions of the bar in pixels.
            is_player: If True, uses fixed 'pos'. If False, follows the node.
        """
        super().__init__(node)
        self.width = width
        self.height = height
        self.pos = pos

        self.is_player = is_player
        self.max_health = max_health
        self.display_health = max_health
        self.shrink_speed = shrink_speed

    def update(self, dt: float = 0.0) -> None:
        """Syncs the visual display health with the Health component logic."""
        health_comp = getattr(self.node, "health", None)
        if health_comp:
            self.display_health = health_comp.current

    def draw(self, screen: pygame.Surface, camera: Optional[Any] = None) -> None:
        """Renders the background and foreground health rectangles."""
        health_comp = getattr(self.node, "health", None)
        if not health_comp:
            return

        # Optimization: Hide enemy health bars if they are at full health
        if not self.is_player and self.display_health >= self.max_health:
            return

        # Calculate Screen Coordinates
        if self.is_player:
            x, y = self.pos
        else:
            # Anchor bar above the entity's head in world space
            x = self.node.rect.centerx - self.width // 2
            y = self.node.rect.top - 8
            if camera:
                x -= camera.x
                y -= camera.y

        # Draw Background (The 'Empty' Bar)
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(screen, GRAY, bg_rect)

        # Draw Foreground (The 'Current' Health)
        ratio = self.display_health / self.max_health
        if ratio > 0:
            fg_width = int(self.width * ratio)
            fg_rect = pygame.Rect(x, y, fg_width, self.height)

            # Dynamic coloring: Green for healthy, Red for critical
            color = GREEN if ratio > 0.3 else RED
            pygame.draw.rect(screen, color, fg_rect)
