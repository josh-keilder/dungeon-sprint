import copy

import pygame

from items.item_texture_data import crate_texture_data
from systems.animation import advance_animation, new_animation
from systems.assets import load_animations, load_image

# Chest art
CHEST_IMAGE_PATH = "Assets/Objects/chest_1.png"

# Crate breaking: a quick squash before the debris burst
CRATE_IMPACT_FRAMES = (2, 3)  # squash frames played on a hit: wide, then flattened
CRATE_IMPACT_SPEED = 20  # impact frames per second


# Item data: templates in the item database, and stacks in the inventory
class Item:
    def __init__(
        self,
        item_id,
        name=None,
        animations=None,
        description=None,
        quantity=1,
        max_stack=99,
        animation_speed=4,
        value_text=None,
    ):
        self.id = item_id
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
        item_id,
        name=None,
        animations=None,
        description=None,
        slot=None,
        bonuses=None,
        value_text=None,
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            animations=animations,
            description=description,
            quantity=1,
            max_stack=1,
            value_text=value_text,
        )
        self.slot = slot
        self.bonuses = bonuses


# World sprites: things placed on a floor
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

    def update(self, dt):
        self.image = advance_animation(self.animation, dt)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))


class Chest(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = load_image(CHEST_IMAGE_PATH)
        self.rect = self.image.get_frect(topleft=pos)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))


class Crate(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)

        # Art: frame 0 is the resting crate
        self.frames = load_animations(crate_texture_data)["crate"]
        self.image = self.frames[0]
        self.rect = self.image.get_frect(topleft=pos)

        # Breaking: solid -> breaking (impact frames) -> done_breaking (the level acts)
        self.breaking = False
        self.done_breaking = False
        self.break_time = 0.0

    def update(self, dt):
        if not self.breaking:
            return

        self.break_time += dt
        step = int(self.break_time * CRATE_IMPACT_SPEED)

        if step >= len(CRATE_IMPACT_FRAMES):
            self.done_breaking = True
            return

        self.image = self.frames[CRATE_IMPACT_FRAMES[step]]

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

    def start_breaking(self):
        self.breaking = True
        self.image = self.frames[CRATE_IMPACT_FRAMES[0]]
