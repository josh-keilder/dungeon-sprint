from engine.core.assets import load_animations
from game.data.constants import TILE_SIZE
from game.data.player_data import PLAYER_DATA
from game.data.textures.player_texture_data import player_texture_data
from game.entities.player.player import Player


def load_player(spawn_pos):
    player_animations = load_animations(player_texture_data, crop_size=TILE_SIZE)

    return Player(PLAYER_DATA, player_animations, pos=spawn_pos)
