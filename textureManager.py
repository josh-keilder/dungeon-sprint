import pygame
from settings import *
from texturedata import atlas_texture_data, solo_texture_data, player_texture_data

class TextureManager:
    def __init__(self):
        pass
    def gen_solo_textures(self) -> dict:
        textures = {}

        for name, data in solo_texture_data.items():
            textures[name] = pygame.transform.scale(pygame.image.load(data['file_path']).convert_alpha(), (data['size']) )
        return textures
    def gen_atlas_textures(self, filepath) -> dict:
        textures = {}

        atlas_img = pygame.image.load(filepath).convert_alpha()

        for name, data in atlas_texture_data.items():
            x = data['position'][0] * TILESIZE
            y = data['position'][1] * TILESIZE
            w, h = data['size'] # unpacks the size tuple
            textures[name] = atlas_img.subsurface(pygame.Rect(x, y, w, h))

            if data.get('type') == 'player':
                textures[name] = pygame.transform.scale(textures[name], (w * 2, h * 2))        
        return textures    

    def gen_player_textures(self) -> dict:
        textures = {}

        for name, data in player_texture_data.items():
            player_img = pygame.image.load(data['file_path']).convert_alpha()
            w, h = data['size'] # unpacks the size tuple
            frames = data['frames']
            row = data['position'][1]
            textures[name] = []

            for i in range(frames):
                x = i * w
                y = row * h
                frame = player_img.subsurface(pygame.Rect(x, y, w, h))
                textures[name].append(frame)
        return textures

