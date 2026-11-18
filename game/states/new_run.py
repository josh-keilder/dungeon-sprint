from game.states.run import Run


def start_new_run(game_state_manager):
    new_run = Run(game_state_manager)

    game_state_manager.add_state("run", new_run)
