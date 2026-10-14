import pygame

WINDOW_TITLE = "Dungeon Sprint"


def create_window(width, height, fullscreen):
    pygame.display.set_caption(WINDOW_TITLE)

    display_flags = pygame.SCALED

    if fullscreen:
        display_flags |= pygame.FULLSCREEN

    return pygame.display.set_mode((width, height), display_flags)
