import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from sprites import FloorTile, WallTile, ObjTile

# if hasattr(layer,'data'): # auto way
class MapLoader:
    def __init__(self):
        pass

    def load_map(self, file_path):
        tmx_data = load_pygame(file_path)
        for layer in tmx_data.visible_layers:
            if layer.name in ('Floor', 'Walls', 'Decor and Doors'): # Manual way
                if layer.name == 'Walls':
                    for x, y, surf in layer.tiles():
                        pos = x * TILESIZE, y * TILESIZE
                        WallTile(groups= self.sprites, image=surf, pos= pos)
                elif layer.name == 'Floor':
                    for x, y, surf in layer.tiles():
                        pos = x * TILESIZE, y * TILESIZE
                        FloorTile(groups= self.sprites, image=surf, pos= pos)
                elif layer.name == 'Decor and Doors':
                    for x, y, surf in layer.tiles():
                        pos = x * TILESIZE, y * TILESIZE
                        ObjTile(groups= self.sprites, image=surf, pos= pos)
        for obj in tmx_data.objects:
            print(obj)
    def get_player_pos(self, file_path):
        tmx_data = load_pygame(file_path)
        for obj in tmx_data.objects:
            if obj.name == 'Player':
                pos_x = obj.x
                pos_y = obj.y
        player_pos = (pos_x, pos_y)
        
        return player_pos
