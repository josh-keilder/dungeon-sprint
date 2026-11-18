import pygame

from engine.io.input import mouse_click_pos, move_direction, pressed_actions

# Key bindings
MOVE_KEYS = (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s)  # left, right, up, down
ACTION_KEYS = {
    "roll": pygame.K_SPACE,
    "interact": pygame.K_f,
    "heal": pygame.K_q,
    "inventory": pygame.K_e,
    "pause": pygame.K_ESCAPE,
    "debug": pygame.K_p,
}


def read_input():
    intent = pressed_actions(pygame.key.get_just_pressed(), ACTION_KEYS)
    intent["move"] = move_direction(pygame.key.get_pressed(), *MOVE_KEYS)
    intent["mouse_left_click"] = mouse_click_pos()
    return intent
