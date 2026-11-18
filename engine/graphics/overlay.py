import pygame

# A screen-sized sheet of one color, drawn over everything to dim or fade the screen


def new_overlay(size, color, alpha=255):
    overlay = pygame.Surface(size, pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    return overlay
