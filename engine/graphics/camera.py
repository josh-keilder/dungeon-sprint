import pygame

# A camera is a Rect: the part of the world that's visible, in world pixels


def new_camera(view_size):
    return pygame.Rect((0, 0), view_size)


def center_camera(camera, pos):
    camera.center = pos


def is_on_screen(camera, target_rect):
    return camera.colliderect(target_rect)


def world_to_screen(camera, pos):
    # Where a world position lands on the surface the camera's view is drawn to
    return (pos[0] - camera.x, pos[1] - camera.y)


def rect_to_screen(camera, rect):
    return rect.move(-camera.x, -camera.y)
