import pygame


def read_input() -> dict:
    key_pressed = pygame.key.get_pressed()
    key_just_pressed = pygame.key.get_just_pressed()

    dir_x, dir_y = 0, 0
    if key_pressed[pygame.K_a]:
        dir_x -= 1
    if key_pressed[pygame.K_d]:
        dir_x += 1
    if key_pressed[pygame.K_w]:
        dir_y -= 1
    if key_pressed[pygame.K_s]:
        dir_y += 1
    move = pygame.math.Vector2(dir_x, dir_y)
    if move.length_squared() > 0:
        move.normalize_ip()

    read_left_click = pygame.mouse.get_just_pressed()[0]
    mouse_left_click_pos = None
    if read_left_click:
        mouse_left_click_pos = pygame.mouse.get_pos()

    return {
        "move": move,
        "roll": key_just_pressed[pygame.K_SPACE],
        "interact": key_just_pressed[pygame.K_f],
        "heal": key_just_pressed[pygame.K_q],
        "inventory": key_just_pressed[pygame.K_e],
        "pause": key_just_pressed[pygame.K_ESCAPE],
        "debug": key_just_pressed[pygame.K_p],
        "mouse_left_click": mouse_left_click_pos,
    }
