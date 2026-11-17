import pygame

from engine.graphics.animation import advance_animation, new_animation

# Animated decor playback: flames read better slow
DECOR_ANIMATION_SPEED = 6  # frames per second


class WallTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)


class DecorTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))


class AnimatedDecor(pygame.sprite.Sprite):
    def __init__(self, groups, frames, pos, start_index):
        super().__init__(groups)
        self.animation = new_animation({"loop": frames}, "loop", DECOR_ANIMATION_SPEED)
        self.animation["index"] = start_index
        self.image = frames[start_index]
        self.rect = self.image.get_frect(topleft=pos)

    def update(self, dt):
        self.image = advance_animation(self.animation, dt)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))


class Door(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)
        self.pos = pygame.math.Vector2(pos)
        self.door_id = None
        self.key = None

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
