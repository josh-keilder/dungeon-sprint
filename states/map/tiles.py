import pygame

from globals import BLUE
from systems import debug
from systems.camera import camera
from systems.hitbox import draw_hitbox


class WallTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

        if debug.show_hitboxes:
            draw_hitbox(screen, self.image, self.rect, camera, BLUE)


class DecorTile(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))


class Door(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)
        self.pos = pygame.math.Vector2(pos)
        self.door_id = None

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
