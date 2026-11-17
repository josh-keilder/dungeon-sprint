import pygame

# The size the game draws at (set by create_window); the window may be letterboxed
_screen_size = None


def create_window(screen_size, fullscreen, title):
    global _screen_size
    _screen_size = screen_size
    pygame.display.set_caption(title)

    display_flags = pygame.OPENGL | pygame.DOUBLEBUF
    size = screen_size
    if fullscreen:
        display_flags |= pygame.FULLSCREEN
        size = (0, 0)  # the desktop's resolution

    return pygame.display.set_mode(size, display_flags)


def letterbox(window_size):
    screen_width, screen_height = _screen_size
    window_width, window_height = window_size
    scale = min(window_width / screen_width, window_height / screen_height)
    left = (window_width - screen_width * scale) / 2
    top = (window_height - screen_height * scale) / 2
    return left, top, scale


def get_mouse_pos():
    x, y = pygame.mouse.get_pos()
    left, top, scale = letterbox(pygame.display.get_window_size())
    return (int((x - left) / scale), int((y - top) / scale))
