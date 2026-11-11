import pygame


def make_outline(image, color):
    mask = pygame.mask.from_surface(image)
    outline_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)

    for component in mask.connected_components():
        for point in component.outline():
            outline_surface.set_at(point, color)

    outline_surface.set_colorkey((0, 0, 0))
    return outline_surface


def draw_outline(screen, outline_surface, pos):
    x, y = pos

    screen.blit(outline_surface, (x - 1, y))
    screen.blit(outline_surface, (x + 1, y))
    screen.blit(outline_surface, (x, y - 1))
    screen.blit(outline_surface, (x, y + 1))
