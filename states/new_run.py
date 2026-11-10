from globals import DUNGEON_LEVEL_ONE
from states.map.level import Level


def start_new_run(game_state_manager):
    new_level = Level(game_state_manager, DUNGEON_LEVEL_ONE)

    game_state_manager.add_state("level", new_level)
