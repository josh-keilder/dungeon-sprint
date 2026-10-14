import pygame

_MASK_CACHE = {}


def get_mask(image):
    if image not in _MASK_CACHE:
        _MASK_CACHE[image] = pygame.mask.from_surface(image)
    return _MASK_CACHE[image]


def sprites_overlap(first_sprite, second_sprite):
    offset = (second_sprite.rect.x - first_sprite.rect.x, second_sprite.rect.y - first_sprite.rect.y)
    return get_mask(first_sprite.image).overlap(get_mask(second_sprite.image), offset) is not None


def draw_hitbox(screen, image, rect, camera, color):
    offset_x = rect.x - (camera.x if camera else 0)
    offset_y = rect.y - (camera.y if camera else 0)

    for point in get_mask(image).outline():
        screen.set_at((int(offset_x + point[0]), int(offset_y + point[1])), color)
