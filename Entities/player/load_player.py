from globals import TILESIZE
from Entities.player.player import Player
from Entities.player.playerTextureData import player_texture_data
from systems.assets import load_animations


def load_player(spawn_pos) -> object:
    player_textures = load_animations(player_texture_data, crop_size=TILESIZE)

    return Player(animations=player_textures, pos=spawn_pos)
