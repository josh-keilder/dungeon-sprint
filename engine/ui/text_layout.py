from engine.ui.theme import get_theme

# Text is placed by its visible ink (get_bounding_rect), not by its surface: a rendered
# surface has empty space above and below the letters, so lining up surfaces would leave
# text visibly off-center. Centered positions are snapped to the theme's pixel grid.


def snap_to_grid(value):
    scale = get_theme("pixel_scale")
    return value // scale * scale


def centered_text_x(text_surface, center_x):
    ink = text_surface.get_bounding_rect()
    return snap_to_grid(center_x - ink.centerx)


def centered_text_y(text_surface, center_y):
    ink = text_surface.get_bounding_rect()
    return snap_to_grid(center_y - ink.centery)


def bottom_right_text_pos(text_surface, right, bottom):
    ink = text_surface.get_bounding_rect()
    return (right - ink.right, bottom - ink.bottom)
