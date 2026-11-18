import pygame

from engine.ui.theme import get_theme

# Enemy health bars: a border around an empty bar with a fill, colors from the theme
HEALTH_BAR_BORDER = 1  # pixels on every side


def draw_health_bar(screen, health, x, y, width, height):
    pygame.draw.rect(
        screen,
        get_theme("health_bar_border_color"),
        (
            x - HEALTH_BAR_BORDER,
            y - HEALTH_BAR_BORDER,
            width + 2 * HEALTH_BAR_BORDER,
            height + 2 * HEALTH_BAR_BORDER,
        ),
    )

    pygame.draw.rect(screen, get_theme("health_bar_empty_color"), (x, y, width, height))

    fill_width = int(width * health["current"] / health["maximum"])

    if health["current"] > 0:
        fill_width = max(1, fill_width)

    if fill_width > 0:
        pygame.draw.rect(
            screen, get_theme("health_bar_fill_color"), (x, y, fill_width, height)
        )
