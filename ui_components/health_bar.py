import pygame

from globals import PALETTE_BLOOD, PALETTE_SHADOW, PALETTE_VOID

HEALTH_BAR_BORDER = 1


def draw_health_bar(screen, health, x, y, width, height):
    pygame.draw.rect(
        screen,
        PALETTE_VOID,
        (
            x - HEALTH_BAR_BORDER,
            y - HEALTH_BAR_BORDER,
            width + 2 * HEALTH_BAR_BORDER,
            height + 2 * HEALTH_BAR_BORDER,
        ),
    )

    pygame.draw.rect(screen, PALETTE_SHADOW, (x, y, width, height))

    fill_width = int(width * health["current"] / health["max_health"])

    if health["current"] > 0:
        fill_width = max(1, fill_width)

    if fill_width > 0:
        pygame.draw.rect(screen, PALETTE_BLOOD, (x, y, fill_width, height))
