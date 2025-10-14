from globals import *
from ui_objects.camera import camera_start
from Characters.player.player import Player
from pytmx.util_pygame import load_pygame

def load_player(self, groups) -> object:
    # Loads and creates the player and makes sure our camera starts with the player in the center
    player_textures = Player.gen_player_textures(self)
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