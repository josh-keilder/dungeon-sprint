import pygame

from engine.core.assets import load_animations, load_image
from engine.graphics.animation import advance_animation, new_animation
from engine.graphics.camera import world_to_screen
from items.item_texture_data import crate_texture_data

# Chest art
CHEST_IMAGE_PATH = "Assets/Objects/chest_1.png"

# Crate breaking: a quick squash before the debris burst
CRATE_IMPACT_FRAMES = (2, 3)  # squash frames played on a hit: wide, then flattened
CRATE_IMPACT_SPEED = 20  # impact frames per second


# World sprites: things placed on a floor
class GroundItem(pygame.sprite.Sprite):
    def __init__(self, groups, pos, item, quantity):
        super().__init__(groups)
        self.item = item.clone()
        self.item.quantity = quantity
        self.animation = new_animation(item.animations, "idle", item.animation_speed)
        self.image = item.image
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        self.image = advance_animation(self.animation, dt)

    def draw(self, screen, camera):
        screen.blit(self.image, world_to_screen(camera, self.rect.topleft))


class Chest(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = load_image(CHEST_IMAGE_PATH)
        self.rect = self.image.get_frect(topleft=pos)

    def draw(self, screen, camera):
        screen.blit(self.image, world_to_screen(camera, self.rect.topleft))


class Crate(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)

        # Art: frame 0 is the resting crate
        self.frames = load_animations(crate_texture_data)["crate"]
        self.image = self.frames[0]
        self.rect = self.image.get_frect(topleft=pos)

        # Breaking: solid -> breaking (impact frames) -> done_breaking (the floor acts)
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
        screen.blit(self.image, world_to_screen(camera, self.rect.topleft))

    def start_breaking(self):
        self.breaking = True
        self.image = self.frames[CRATE_IMPACT_FRAMES[0]]
