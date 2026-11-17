import pygame

# Cache: one mask per image, built on first use
_MASK_CACHE = {}

# The 4 neighbors used to grow a mask by one pixel
NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def get_mask(image):
    if image not in _MASK_CACHE:
        _MASK_CACHE[image] = pygame.mask.from_surface(image)
    return _MASK_CACHE[image]


def images_overlap(first_image, first_pos, second_image, second_pos):
    offset = (int(second_pos[0] - first_pos[0]), int(second_pos[1] - first_pos[1]))
    return get_mask(first_image).overlap(get_mask(second_image), offset) is not None


def draw_hitbox(screen, image, rect, camera, color):
    offset_x = rect.x - (camera.x if camera else 0)
    offset_y = rect.y - (camera.y if camera else 0)

    for point in get_mask(image).outline():
        screen.set_at((int(offset_x + point[0]), int(offset_y + point[1])), color)


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


def grow_mask(mask):
    grown = mask.copy()
    for offset in NEIGHBORS:
        grown.draw(mask, offset)

    return grown
