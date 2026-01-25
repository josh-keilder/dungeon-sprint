from globals import *
from pytmx.util_pygame import load_pygame
from states.map.tiles import FloorTile, WallTile, ObjTile, Door

layer_names = [
    'Floor', 
    'Walls', 
    'Decor and Doors',
    'Door Tiles'
]

def load_map(sprites_group, wall_tiles_group, file_path):
    tmx_data = load_pygame(file_path)
    for layer in tmx_data.visible_layers:
        if layer.name in layer_names: 
            if layer.name == 'Walls':
                for x, y, surf in layer.tiles():
                    pos = (x * TILESIZE, y * TILESIZE)
                    WallTile(groups= wall_tiles_group, image=surf, pos= pos)

            if layer.name == 'Floor':
                for x, y, surf in layer.tiles():
                    pos = (x * TILESIZE, y * TILESIZE)
                    FloorTile(groups= sprites_group, image=surf, pos= pos)

            if layer.name == 'Decor':
                for x, y, surf in layer.tiles():
                    pos = (x * TILESIZE, y * TILESIZE)
                    ObjTile(groups= sprites_group, image=surf, pos= pos)

            if layer.name == 'Doors':
                for x, y, surf in layer.tiles():
                    pos = (x * TILESIZE, y * TILESIZE)
                    Door(groups= sprites_group, image=surf, pos= pos)
            