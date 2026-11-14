import os
import sys

import pygame

from globals import (
    FONT_PATH,
    LEVEL_ORDER,
    PALETTE_AZURE,
    PALETTE_BLOOD,
    PALETTE_GOLD,
    PALETTE_ICE,
    PALETTE_VOID,
    TILE_SIZE,
)
from items.item_database import initialize_item_database
from states.map.map_loader import load_level_data

PREVIEW_SCALE = 2
PREVIEW_MARGIN = 2 * TILE_SIZE
LABEL_FONT_SIZE = 8
SPAWN_MARKER_RADIUS = 4
OUTPUT_FOLDER = "map_previews"


def draw_label(surface, font, text, pos):
    label = font.render(text, False, PALETTE_ICE)
    background = label.get_rect(topleft=pos).inflate(2, 2)
    pygame.draw.rect(surface, PALETTE_VOID, background)
    surface.blit(label, pos)


def preview_map(map_path, font, item_database):
    level_data = load_level_data(map_path)
    preview = level_data["map_surface"].copy()

    for group_name in ("decor_tiles", "wall_tiles", "door_tiles", "chests"):
        for sprite in level_data[group_name]:
            preview.blit(sprite.image, sprite.rect.topleft)

    for item_id, center in level_data["placed_items"]:
        item_image = item_database[item_id].image
        preview.blit(item_image, item_image.get_rect(center=center))

    labeled_door_ids = set()
    for door in level_data["door_tiles"]:
        if door.door_id is None or door.door_id in labeled_door_ids:
            continue
        labeled_door_ids.add(door.door_id)
        draw_label(preview, font, door.door_id, door.rect.topleft)

    for enemy_type, positions in level_data["enemy_spawns"].items():
        for pos in positions:
            marker = pygame.Rect(pos, (TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(preview, PALETTE_BLOOD, marker, 1)
            draw_label(preview, font, enemy_type[:3], (pos[0] + 2, pos[1] + 2))

    player_spawn = level_data["player_spawn"]
    pygame.draw.circle(preview, PALETTE_VOID, player_spawn, SPAWN_MARKER_RADIUS + 1)
    pygame.draw.circle(preview, PALETTE_AZURE, player_spawn, SPAWN_MARKER_RADIUS)

    if level_data["exit_rect"] is not None:
        pygame.draw.rect(preview, PALETTE_GOLD, level_data["exit_rect"], 1)

    wall_rects = [wall.rect for wall in level_data["wall_tiles"]]
    bounds = wall_rects[0].unionall(wall_rects[1:])
    bounds = bounds.inflate(2 * PREVIEW_MARGIN, 2 * PREVIEW_MARGIN)
    bounds = bounds.clip(preview.get_rect())

    cropped = preview.subsurface(bounds)
    return pygame.transform.scale_by(cropped, PREVIEW_SCALE)


def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    font = pygame.font.Font(FONT_PATH, LABEL_FONT_SIZE)

    item_database = initialize_item_database()

    map_paths = sys.argv[1:] or list(dict.fromkeys(LEVEL_ORDER))

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    for map_path in map_paths:
        image = preview_map(map_path, font, item_database)
        map_name = os.path.splitext(os.path.basename(map_path))[0]
        output_path = os.path.join(OUTPUT_FOLDER, f"{map_name}.png")
        pygame.image.save(image, output_path)
        print(f"Saved {output_path} ({image.get_width()}x{image.get_height()})")


if __name__ == "__main__":
    main()
