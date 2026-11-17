import pygame

# A camera is a Rect: the part of the world that's visible, in world pixels


def new_camera(view_size):
    return pygame.Rect((0, 0), view_size)


def center_camera(camera, pos):
    camera.center = pos


def is_on_screen(camera, target_rect):
    return camera.colliderect(target_rect)
