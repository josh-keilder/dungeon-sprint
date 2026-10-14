import pygame


def read_input() -> dict:
    keys_held = pygame.key.get_pressed()
    keys_just_pressed = pygame.key.get_just_pressed()

    direction_x, direction_y = 0, 0
    if keys_held[pygame.K_a]:
        direction_x -= 1
    if keys_held[pygame.K_d]:
        direction_x += 1
    if keys_held[pygame.K_w]:
        direction_y -= 1
    if keys_held[pygame.K_s]:
        direction_y += 1
    move_direction = pygame.math.Vector2(direction_x, direction_y)
    if move_direction.length_squared() > 0:
        move_direction.normalize_ip()

    left_button_just_pressed = pygame.mouse.get_just_pressed()[0]
    left_click_pos = None
    if left_button_just_pressed:
        left_click_pos = pygame.mouse.get_pos()

    return {
        "move": move_direction,
        "roll": keys_just_pressed[pygame.K_SPACE],
        "interact": keys_just_pressed[pygame.K_f],
        "heal": keys_just_pressed[pygame.K_q],
        "inventory": keys_just_pressed[pygame.K_e],
        "pause": keys_just_pressed[pygame.K_ESCAPE],
        "debug": keys_just_pressed[pygame.K_p],
        "mouse_left_click": left_click_pos,
    }
