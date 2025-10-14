from globals import *
from ui_objects.camera import camera_start
from Characters.player.player import Player
from pytmx.util_pygame import load_pygame
from Characters.player.playerTextureData import player_texture_data

def load_player(groups) -> object:
    # Loads and creates the player and makes sure our camera starts with the player in the center
    player_textures = gen_player_textures()
    player_pos = get_player_pos(file_path = DUNGEON_LEVEL_ONE)
    player = Player(groups, animations=player_textures, pos = player_pos)
    camera_start(player.rect.center)

    return player

def get_player_pos(file_path) -> tuple:
    tmx_data = load_pygame(file_path)
    for obj in tmx_data.objects:
        if obj.name == 'Player':
            pos_x, pos_y = obj.x, obj.y
    player_pos = (pos_x, pos_y)
        
    return player_pos

def gen_player_textures() -> dict:
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

            # Since the player sprites are 64x64, you have to crop out just the center player to get the hitbox to be the right size
            center_x = (w - 16) // 2
            center_y = (h - 16) // 2
            center_rect = pygame.Rect(center_x, center_y, 16, 16)
            cropped_frame = frame.subsurface(center_rect).copy()

            textures[name].append(cropped_frame)
            
    return textures