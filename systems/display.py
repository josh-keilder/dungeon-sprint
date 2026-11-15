import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH

# Window
WINDOW_TITLE = "Dungeon Sprint"


def create_window(width, height, fullscreen):
    pygame.display.set_caption(WINDOW_TITLE)

    display_flags = pygame.OPENGL | pygame.DOUBLEBUF
    size = (width, height)
    if fullscreen:
        display_flags |= pygame.FULLSCREEN
        size = (0, 0)  # the desktop's resolution

    return pygame.display.set_mode(size, display_flags)


def letterbox(window_size):
    window_width, window_height = window_size
    scale = min(window_width / SCREEN_WIDTH, window_height / SCREEN_HEIGHT)
    left = (window_width - SCREEN_WIDTH * scale) / 2
    top = (window_height - SCREEN_HEIGHT * scale) / 2
    return left, top, scale


def get_mouse_pos():
    x, y = pygame.mouse.get_pos()
    left, top, scale = letterbox(pygame.display.get_window_size())
    return (int((x - left) / scale), int((y - top) / scale))
