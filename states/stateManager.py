import pygame
from globals import *

# Change between screens
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
        self.state_history = []
        self.states = {}

    def add_state(self, name, state_object):
        # Add a new state to the manager
        self.states[name] = state_object

    def get_state(self) -> str:
        return self.states.get(self.currentState, None)
    
    def set_state(self, new_state):
        if self.currentState:
            self.state_history.append(self.currentState)
        self.currentState = new_state

    def get_previous_state(self) -> str:
        # If history is available, return the previous one. Return None if none exists
        if self.state_history:
            return self.state_history[-1]
        return None
    
    def go_back(self):
        # Pop the last state if available
        if self.state_history:
            self.currentState = self.state_history.pop()

    def all_states(self) -> list: # Returns all states currently in the dict
        return list(self.states.keys())
