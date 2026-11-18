import pygame

from engine.ui.theme import get_theme

# A screen title: one line of large text in the theme's font, centered across the screen


def make_title(text, font_size, color, screen_width, y):
    font = pygame.font.Font(get_theme("font_path"), font_size)
    image = font.render(text, False, color)
    pos = ((screen_width - image.get_width()) // 2, y)
    return image, pos
