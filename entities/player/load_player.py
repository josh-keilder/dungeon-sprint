from entities.player.player import Player
from entities.player.player_texture_data import player_texture_data
from globals import TILE_SIZE
from systems.assets import load_animations


def load_player(spawn_pos):
    player_animations = load_animations(player_texture_data, crop_size=TILE_SIZE)

    return Player(animations=player_animations, pos=spawn_pos)
