# Light look
LIGHT_BANDS = 0  # light falls off in this many visible steps; 0 = smooth
# Unlit areas: a little cool, everything stays visible
AMBIENT_LIGHT = (0.70, 0.70, 0.80)
MAX_LIGHT = 1.25  # lights may brighten the art up to this much above its own colors
MAX_LIGHTS = 32  # sent to the shader at once (the shader's arrays use this size)

# Light types: radius in world pixels, color as 0-1 RGB, intensity, and where the
# flame sits from the tile's center (side torches lean left; mirrored ones flip x)
LIGHT_TYPES = {
    "torch": {
        "radius": 90,
        "color": (1.0, 0.62, 0.32),
        "intensity": 0.75,
        "offset": (0, -4),
    },
    "side_torch": {
        "radius": 72,
        "color": (1.0, 0.62, 0.32),
        "intensity": 0.65,
        "offset": (-5, -4),
    },
    "candlestick_1": {
        "radius": 56,
        "color": (1.0, 0.85, 0.50),
        "intensity": 0.6,
        "offset": (0, -5),
    },
    "candlestick_2": {
        "radius": 56,
        "color": (1.0, 0.85, 0.50),
        "intensity": 0.6,
        "offset": (0, -5),
    },
    "player": {
        "radius": 64,
        "color": (0.80, 0.88, 1.0),
        "intensity": 0.2,
        "offset": (0, 0),
    },
}


def flame_position(name, tile_center, flipped):
    offset_x, offset_y = LIGHT_TYPES[name]["offset"]
    if flipped:
        offset_x = -offset_x
    return (tile_center[0] + offset_x, tile_center[1] + offset_y)


def visible_lights(floor_lights, player_center, camera):
    reach = max(light_type["radius"] for light_type in LIGHT_TYPES.values())
    area = camera.inflate(2 * reach, 2 * reach)

    lights = []
    for name, (x, y) in [("player", player_center)] + floor_lights:
        if not area.collidepoint(x, y):
            continue

        light_type = LIGHT_TYPES[name]
        color = tuple(
            channel * light_type["intensity"] for channel in light_type["color"]
        )
        lights.append(((x - camera.x, y - camera.y), light_type["radius"], color))

    return lights[:MAX_LIGHTS]
