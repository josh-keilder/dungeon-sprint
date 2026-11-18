# Light look, handed to the renderer by main.py
LIGHT_BANDS = 0  # light falls off in this many visible steps; 0 = smooth
# Unlit areas: a little cool, everything stays visible
AMBIENT_LIGHT = (0.78, 0.78, 0.86)
MAX_LIGHT = 1.25  # lights may brighten the art up to this much above its own colors

# Light types: radius in world pixels, color as 0-1 RGB, intensity, and where the
# flame sits from the tile's center (side torches lean left; mirrored ones flip x)
LIGHT_TYPES = {
    "torch": {
        "radius": 90,
        "color": (1.0, 0.62, 0.32),
        "intensity": 0.75,
        "offset": (0, -4),
        "flicker": 0.12,
    },
    "side_torch": {
        "radius": 72,
        "color": (1.0, 0.62, 0.32),
        "intensity": 0.65,
        "offset": (-5, -4),
        "flicker": 0.12,
    },
    "candlestick_1": {
        "radius": 56,
        "color": (1.0, 0.85, 0.50),
        "intensity": 0.6,
        "offset": (0, -5),
        "flicker": 0.06,
    },
    "candlestick_2": {
        "radius": 56,
        "color": (1.0, 0.85, 0.50),
        "intensity": 0.6,
        "offset": (0, -5),
        "flicker": 0.06,
    },
    "player": {
        "radius": 64,
        "color": (0.80, 0.88, 1.0),
        "intensity": 0.3,
        "offset": (0, 0),
        "flicker": 0.0,
    },
}
