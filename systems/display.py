import pygame

WINDOW_TITLE = "Dungeon Sprint"


def create_window(width, height, fullscreen):

    pygame.display.set_caption(WINDOW_TITLE)

    flags = pygame.SCALED

    if fullscreen:
        flags |= pygame.FULLSCREEN

    return pygame.display.set_mode((width, height), flags)
