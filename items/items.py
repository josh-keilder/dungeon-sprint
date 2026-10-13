"""
System: Item and Loot Generation
-------------------------------
Defines the data structures and world-space objects for the game's item
system. Uses a Prototype pattern for item instantiation and a static
image cache to optimize texture loading for large numbers of world items.

Classes:
    Item: Base data class for all items.
    EquipmentItem: Specialized item for wearable gear with stats.
    WorldItem: The physical Sprite representation of an item on the ground.
    Chest: An interactable container that rolls loot and spawns WorldItems.
"""

import pygame
from globals import *
import pygame, copy, random
from Components.animationComponent import AnimationComponent


class Item:
    def __init__(
        self,
        id: str,
        type: str = None,
        name: str = None,
        animations: dict = None,
        desc: str = None,
        quantity: int = 1,
        max_stack: int = 99,
        animation_speed: int = 4,
        value: str = None,
    ):
        """
        Base blueprint for an item.
        Note: 'animations' expects a dict of frame lists.
        """
        self.id = id
        self.type = type
        self.name = name
        self.animations = animations
        self.desc = desc
        self.quantity = quantity
        self.max_stack = max_stack
        self.animation_speed = animation_speed
        self.value = value

        self.image = animations.get("idle", [None])[0]

    def clone(self):
        return copy.copy(self)


class EquipmentItem(Item):
    def __init__(
        self,
        id: str,
        name: str = None,
        animations: dict = None,
        desc: str = None,
        slot: str = None,
        bonuses: dict = None,
        ability: str = None,
        value: str = None,
    ):
        """Specialized Item with slot-specific logic and stat modifiers."""
        super().__init__(
            id=id,
            type="equipment",
            name=name,
            animations=animations,
            desc=desc,
            quantity=1,
            max_stack=1,
            value=value,
        )
        self.slot = slot
        self.bonuses = bonuses
        self.ability = ability


class WorldItem(pygame.sprite.Sprite):
    def __init__(self, groups, pos, item_data, quantity):
        """
        The physical entity representing an item in the game world.
        Takes an Item object and wraps it in a Sprite with an AnimationComponent.
        """
        super().__init__(groups)
        self.item_data = item_data.clone()
        self.item_data.quantity = quantity
        self.animations = AnimationComponent(
            node=self,
            animations=item_data.animations,
            start_animation="idle",
            animation_speed=item_data.animation_speed,
        )
        self.image = item_data.image
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self, screen, camera):
        """Renders the item relative to the camera."""
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

    def update(self, dt):
        """Advances the item's visual animation."""
        self.animations.update(dt)


class Chest(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        """Interactable container that spawns WorldItems when opened."""
        super().__init__(groups)
        self.image = CHEST_IMAGE
        self.rect = self.image.get_frect(topleft=pos)
        self.pos = pygame.math.Vector2(pos)

    def draw(self, screen, camera):
        """Renders the chest relative to the camera."""
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
