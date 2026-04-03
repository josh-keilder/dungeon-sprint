from globals import *


# Change between screens
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
        self.state_history = []
        self.states = {}
        self.active_state_object = None

    def add_state(self, name, state_object):
        # Add a new state to the manager
        self.states[name] = state_object

        if name == self.currentState:
            self.active_state_object = state_object

    def get_state(self) -> str:
        return self.active_state_object

    def set_state(self, new_state):
        if new_state not in self.states:
            print(f"Error, State {new_state} does not exist")
            return

        if self.currentState:
            self.state_history.append(self.currentState)
        self.currentState = new_state
        self.active_state_object = self.states[new_state]

        # Keeps the state history to a small size for optimization... don't want a million states saved
        if len(self.state_history) > 3:
            self.state_history.pop(0)

    def get_previous_state(self) -> str:
        # If history is available, return the previous one. Return None if none exists
        if self.state_history:
            return self.state_history[-1]
        return None

    def go_back(self):
        # Pop the last state if available
        if self.state_history:
            self.currentState = self.state_history.pop()
            self.active_state_object = self.states[self.currentState]

    def all_states(self) -> list:  # Returns all states currently in the dict
        return list(self.states.keys())

    def update_screen_reference(self, new_screen):
        for state in self.states.values():
            state.screen = new_screen
