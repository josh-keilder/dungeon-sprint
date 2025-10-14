from globals import *
from pytmx.util_pygame import load_pygame
from states.dungeons.tiles import FloorTile, WallTile, ObjTile

# if hasattr(layer,'data'): # auto way
def load_map(sprites_group, wall_tiles_group, file_path):
    tmx_data = load_pygame(file_path)
    for layer in tmx_data.visible_layers:
        if layer.name in ('Floor', 'Walls', 'Decor and Doors'): # Manual way
            if layer.name == 'Walls':
                for x, y, surf in layer.tiles():
                    if surf:
                        pos = (x * TILESIZE, y * TILESIZE)
                        WallTile(groups= wall_tiles_group, image=surf, pos= pos)
            elif layer.name == 'Floor':
                for x, y, surf in layer.tiles():
                    pos = (x * TILESIZE, y * TILESIZE)
                    FloorTile(groups= sprites_group, image=surf, pos= pos)
            elif layer.name == 'Decor and Doors':
                for x, y, surf in layer.tiles():
                    pos = (x * TILESIZE, y * TILESIZE)
                    ObjTile(groups= sprites_group, image=surf, pos= pos)
