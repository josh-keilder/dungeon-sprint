"""
System: Input Management
-------------------------
A component-based input handler that maps keyboard and mouse events to game actions.
It processes movement, interaction (chests, doors, pickups), and inventory management,
utilizing independent cooldown timers to prevent input spamming.

Classes:
    InputComponent: Bridges Pygame event polling with entity-specific logic.
"""

import pygame
from Components.component import Component
from typing import Any


class InputComponent(Component):
    def __init__(self, node: Any) -> None:
        """Initializes input state, sound references, and interaction cooldowns."""
        super().__init__(node)
        self.node = node

        # --- COOLDOWNS (Seconds) ---
        self.inventory_cooldown = 0.0

        self.show_inventory = False

    def update(self, dt: float) -> None:
        """
        Polls for active keys and executes relevant logic branches.
        Handles high-level system inputs and updates cooldown timers.
        """
        keys = pygame.key.get_pressed()

        # Run Specialized Input Handlers
        self.inventory_input(keys, dt)

        # Global Cooldown Decay
        self.inventory_cooldown = max(0, self.inventory_cooldown - dt)

    def inventory_input(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:
        """Manages inventory visibility and internal click handling."""
        if keys[pygame.K_e] and self.inventory_cooldown <= 0:
            self.show_inventory = not self.show_inventory
            self.inventory_cooldown = 0.3

        if self.show_inventory:
            mouse_clicked = pygame.mouse.get_pressed()
            if mouse_clicked[0] and self.inventory_cooldown <= 0:
                inv = getattr(self.node, "inventory", None)
                if inv:
                    inv.handle_click(pygame.mouse.get_pos())
                    self.inventory_cooldown = 0.2
