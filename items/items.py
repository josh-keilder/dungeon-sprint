import copy

import pygame

from systems.animation import advance_animation, new_animation
from systems.assets import load_image


class Item:
    def __init__(
        self,
        id: str,
        name: str = None,
        animations: dict = None,
        description: str = None,
        quantity: int = 1,
        max_stack: int = 99,
        animation_speed: int = 4,
        value_text: str = None,
    ):
        self.id = id
        self.name = name
        self.animations = animations
        self.description = description
        self.quantity = quantity
        self.max_stack = max_stack
        self.animation_speed = animation_speed
        self.value_text = value_text

        self.image = animations.get("idle", [None])[0]

    def clone(self):
        return copy.copy(self)


class EquipmentItem(Item):
    def __init__(
        self,
        id: str,
        name: str = None,
        animations: dict = None,
        description: str = None,
        slot: str = None,
        bonuses: dict = None,
        value_text: str = None,
    ):
        super().__init__(
            id=id,
            name=name,
            animations=animations,
            description=description,
            quantity=1,
            max_stack=1,
            value_text=value_text,
        )
        self.slot = slot
        self.bonuses = bonuses


class WorldItem(pygame.sprite.Sprite):
    def __init__(self, groups, pos, item_data, quantity):
        super().__init__(groups)
        self.item_data = item_data.clone()
        self.item_data.quantity = quantity
        self.animation = new_animation(
            item_data.animations, "idle", item_data.animation_speed
        )
        self.image = item_data.image
        self.rect = self.image.get_rect(center=pos)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

    def update(self, dt):
        self.image = advance_animation(self.animation, dt)


CHEST_IMAGE_PATH = "Assets/Objects/chest_1.png"


class Chest(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = load_image(CHEST_IMAGE_PATH)
        self.rect = self.image.get_frect(topleft=pos)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
