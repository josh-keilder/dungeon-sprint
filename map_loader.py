import pygame
from settings import *

from sprite import TileEntity
import csv



class MapLoader:
    def __init__(self):
        self.load_map = self.load_csv_map()
    def load_csv_map(self, file_path):
        with open(file_path) as file:
            reader = csv.reader(file)
            return [[int(cell) for cell in row] for row in reader]
    # Takes the tilemap and makes tile entities
    def create_tiles(self):
        for row_index, row in enumerate(self.tilemap):
            for col_index, tile in enumerate(row):
                if tile != -1:
                    image = self.atlas_textures[tile]
                    tile_entity = TileEntity([self.sprites], image, position = (col_index * TILESIZE, row_index * TILESIZE))
                    self.sprites.change_layer(tile_entity,0)
        