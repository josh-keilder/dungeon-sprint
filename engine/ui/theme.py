from engine.io import sound

# The look every engine widget reads. The game calls set_theme(...) once at startup,
# before any widget is built; keys it doesn't set keep these plain defaults.
_theme = {
    # Text
    "font_path": None,  # None = pygame's built-in font
    "font_size": 24,
    "text_color": (255, 255, 255),
    "text_outline_color": (0, 0, 0),
    "hover_color": (255, 200, 0),
    # Pixel grid: centered text snaps to it, text outlines are one grid step wide
    "pixel_scale": 1,
    # Buttons and sliders
    "button_outline_color": (255, 255, 255),
    "slider_empty_color": (60, 60, 60),
    "hover_sound": None,  # sound names for engine.io.sound; None = silent
    "click_sound": None,
    # Health bars
    "health_bar_border_color": (0, 0, 0),
    "health_bar_empty_color": (60, 60, 60),
    "health_bar_fill_color": (200, 40, 40),
}


def set_theme(**values):
    for key, value in values.items():
        if key not in _theme:
            raise KeyError(f"Unknown theme key: {key}")
        _theme[key] = value


def get_theme(key):
    return _theme[key]


def play_theme_sound(key):
    name = _theme[key]
    if name is not None:
        sound.play_sfx(name)
