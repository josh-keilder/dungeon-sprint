"""
System: State Management
------------------------
Orchestrates transitions between different game modes (e.g., Main Menu,
Settings, Gameplay). Maintains a limited history of previous states to
allow for easy "back" navigation.

Classes:
    GameStateManager: Manages the registration, switching, and retrieval of active game states.
"""

from globals import *


class GameStateManager:
    def __init__(self, currentState):
        """
        Initializes the manager with a starting state.

        Args:
            currentState (str): The name of the initial active state.
        """
        self.currentState = currentState
        self.state_history = []
        self.states = {}
        self.active_state_object = None

    def add_state(self, name, state_object):
        """Registers a new state object and sets it as active if names match."""
        self.states[name] = state_object

        if name == self.currentState:
            self.active_state_object = state_object

    def get_state(self):
        """Returns the currently active state object."""
        return self.active_state_object

    def set_state(self, new_state):
        """
        Transitions to a new state and records the previous one in history.
        Limits history to the 3 most recent states for memory optimization.
        """
        if new_state not in self.states:
            print(f"Error: State '{new_state}' does not exist.")
            return

        if self.currentState:
            self.state_history.append(self.currentState)

        self.currentState = new_state
        self.active_state_object = self.states[new_state]

        # History Capping: Keep history lean to avoid unnecessary growth
        if len(self.state_history) > 3:
            self.state_history.pop(0)

    def get_previous_state(self) -> str:
        """Returns the name of the last visited state, or None if history is empty."""
        if self.state_history:
            return self.state_history[-1]
        return None

    def go_back(self):
        """Reverts the current state to the most recent entry in the history stack."""
        if self.state_history:
            self.currentState = self.state_history.pop()
            self.active_state_object = self.states[self.currentState]

    def all_states(self) -> list:
        """Returns a list of all registered state names."""
        return list(self.states.keys())

    def update_screen_reference(self, new_screen):
        """Propagates a new display surface reference to all registered states."""
        for state in self.states.values():
            state.screen = new_screen
