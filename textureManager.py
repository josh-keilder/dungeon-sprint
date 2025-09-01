import pygame
from settings import *
from texturedata import atlas_texture_data, solo_texture_data


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

        # Old code - atlas_img = pygame.transform.scale(pygame.image.load(filepath).convert_alpha(), (TILESIZE*16, TILESIZE*16))
        atlas_img = pygame.image.load(filepath).convert_alpha()

        for name, data in atlas_texture_data.items():
            x = data['position'][0] * PLAYER_SPRITESIZE
            y = data['position'][1] * PLAYER_SPRITESIZE
            w, h = data['size'] # unpacks the size tuple
            textures[name] = atlas_img.subsurface(pygame.Rect(x, y, w, h))

            # Old code - textures[name] = pygame.Surface.subsurface(atlas_img, pygame.Rect(data['position'][0]*SPRITESIZE, data['position'][1]*SPRITESIZE, data['size']))
        
        return textures    


