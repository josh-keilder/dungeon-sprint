import pygame
from globals import GRAY, GREEN, RED

LOW_HEALTH_RATIO = 0.3


def draw_health_bar(screen, health, x, y, width, height):
    ratio = health["current"] / health["max_health"]

    pygame.draw.rect(screen, GRAY, pygame.Rect(x, y, width, height))

    if ratio > 0:
        fill_width = int(width * ratio)

        color = GREEN if ratio > LOW_HEALTH_RATIO else RED

        pygame.draw.rect(screen, color, pygame.Rect(x, y, fill_width, height))
