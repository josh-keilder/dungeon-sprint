import csv
import pygame
from settings import *



class MapLoader:
    def __init__(self):
        self.load_map = self.load_csv_map()
    def load_csv_map(file_path):
        
        
        with open(file_path) as file:
            reader = csv.reader(file)
            return [[int(cell) for cell in row] for row in reader]
        