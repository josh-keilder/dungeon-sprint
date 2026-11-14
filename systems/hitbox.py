import pygame

_MASK_CACHE = {}

NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def grow_mask(mask):
    grown = mask.copy()
    for offset in NEIGHBORS:
        grown.draw(mask, offset)

    return grown


def draw_highlight(screen, sprites, camera, color):
    rects = [pygame.Rect(sprite.rect) for sprite in sprites]
    area = rects[0].unionall(rects[1:]).inflate(4, 4)

    # One combined shape for every sprite (both halves of a door)
    shape = pygame.Mask(area.size)
    for sprite in sprites:
        offset = (int(sprite.rect.x - area.x), int(sprite.rect.y - area.y))
        shape.draw(get_mask(sprite.image), offset)

    # Close 1-pixel gaps (the chest's lid seam): grow, then shrink back
    shape = grow_mask(shape)
    outside = shape.copy()
    outside.invert()
    shape = grow_mask(outside)
    shape.invert()

    # The ring just outside the shape
    ring = grow_mask(shape)
    ring.erase(shape, (0, 0))

    ring_image = ring.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    screen.blit(ring_image, (area.x - camera.x, area.y - camera.y))


def get_mask(image):
    if image not in _MASK_CACHE:
        _MASK_CACHE[image] = pygame.mask.from_surface(image)
    return _MASK_CACHE[image]


def sprites_overlap(first_sprite, second_sprite):
    offset = (
        second_sprite.rect.x - first_sprite.rect.x,
        second_sprite.rect.y - first_sprite.rect.y,
    )
    return (
        get_mask(first_sprite.image).overlap(get_mask(second_sprite.image), offset)
        is not None
    )


def draw_hitbox(screen, image, rect, camera, color):
    offset_x = rect.x - (camera.x if camera else 0)
    offset_y = rect.y - (camera.y if camera else 0)

    for point in get_mask(image).outline():
        screen.set_at((int(offset_x + point[0]), int(offset_y + point[1])), color)
