from globals import *
from Components.component import Component
from typing import Any


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
