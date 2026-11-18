import pygame

from engine.graphics.display import get_mouse_pos

# Generic input helpers; each game defines its own bindings and actions


def move_direction(keys_held, left, right, up, down):
    # A unit vector from four held keys (zero when none or opposite ones are held)
    direction = pygame.Vector2(
        keys_held[right] - keys_held[left], keys_held[down] - keys_held[up]
    )
    if direction.length_squared() > 0:
        direction.normalize_ip()
    return direction


def pressed_actions(keys_just_pressed, bindings):
    # {action: key} -> {action: pressed this frame}
    return {action: keys_just_pressed[key] for action, key in bindings.items()}


def mouse_click_pos(button=0):
    # Where the mouse button was just pressed (screen pixels), or None
    if pygame.mouse.get_just_pressed()[button]:
        return get_mouse_pos()
    return None
