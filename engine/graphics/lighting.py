import math

# The shader's light arrays hold this many; visible_lights never returns more
MAX_LIGHTS = 32
# Flicker: two waves at speeds that don't line up, so the wobble never quite repeats
FLICKER_SPEEDS = (7.0, 12.7)  # radians per second

# A light type is a dict: "radius" (world pixels), "color" (0-1 RGB), "intensity",
# "offset" (the flame's x, y from its tile's center) and "flicker" (0 = steady)


def flame_position(light_type, tile_center, flipped):
    offset_x, offset_y = light_type["offset"]
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


def visible_lights(lights, light_types, camera, time):
    # lights: (type name, world position) pairs. Returns the ones near the camera as
    # (position on the world surface, radius, color), at most MAX_LIGHTS, in list order
    reach = max(light_type["radius"] for light_type in light_types.values())
    area = camera.inflate(2 * reach, 2 * reach)

    visible = []
    for name, (x, y) in lights:
        if not area.collidepoint(x, y):
            continue

        light_type = light_types[name]
        flicker = 1 + light_type["flicker"] * flicker_wave(time, (x, y))
        intensity = light_type["intensity"] * flicker
        color = tuple(channel * intensity for channel in light_type["color"])
        visible.append(((x - camera.x, y - camera.y), light_type["radius"], color))

    return visible[:MAX_LIGHTS]


def light_blockers(map_size, tiles, tile_size):
    # One byte per map tile, row by row: 1 where light can't pass
    columns, rows = map_size[0] // tile_size, map_size[1] // tile_size
    mask = bytearray(columns * rows)
    for tile in tiles:
        column, row = int(tile.rect.x // tile_size), int(tile.rect.y // tile_size)
        mask[row * columns + column] = 1

    return (columns, rows), bytes(mask)
