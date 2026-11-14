from states.map.level import Level


def start_new_run(game_state_manager):
    new_level = Level(game_state_manager)

    game_state_manager.add_state("level", new_level)
