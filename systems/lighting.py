import math

from constants import TILE_SIZE

# Light look
LIGHT_BANDS = 0  # light falls off in this many visible steps; 0 = smooth
# Unlit areas: a little cool, everything stays visible
AMBIENT_LIGHT = (0.78, 0.78, 0.86)
MAX_LIGHT = 1.25  # lights may brighten the art up to this much above its own colors
MAX_LIGHTS = 32  # sent to the shader at once (the shader's arrays use this size)
# Flicker: two waves at speeds that don't line up, so the wobble never quite repeats
FLICKER_SPEEDS = (7.0, 12.7)  # radians per second

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


def flame_position(name, tile_center, flipped):
    offset_x, offset_y = LIGHT_TYPES[name]["offset"]
    if flipped:
        offset_x = -offset_x
    return (tile_center[0] + offset_x, tile_center[1] + offset_y)


def flicker_wave(time, position):
    # -1 to 1; each light gets its own phase from where it stands
    phase = position[0] * 0.37 + position[1] * 0.73
    slow, fast = FLICKER_SPEEDS
    slow_wave = math.sin(time * slow + phase)
    fast_wave = math.sin(time * fast + phase * 2.3)
    return 0.6 * slow_wave + 0.4 * fast_wave


def visible_lights(floor_lights, player_center, camera, time):
    reach = max(light_type["radius"] for light_type in LIGHT_TYPES.values())
    area = camera.inflate(2 * reach, 2 * reach)

    lights = []
    for name, (x, y) in [("player", player_center)] + floor_lights:
        if not area.collidepoint(x, y):
            continue

        light_type = LIGHT_TYPES[name]
        flicker = 1 + light_type["flicker"] * flicker_wave(time, (x, y))
        intensity = light_type["intensity"] * flicker
        color = tuple(channel * intensity for channel in light_type["color"])
        lights.append(((x - camera.x, y - camera.y), light_type["radius"], color))

    return lights[:MAX_LIGHTS]


def light_blockers(map_size, tiles):
    # One byte per map tile, row by row: 1 where light can't pass
    columns, rows = map_size[0] // TILE_SIZE, map_size[1] // TILE_SIZE
    mask = bytearray(columns * rows)
    for tile in tiles:
        column, row = int(tile.rect.x // TILE_SIZE), int(tile.rect.y // TILE_SIZE)
        mask[row * columns + column] = 1

    return (columns, rows), bytes(mask)
