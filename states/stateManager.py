import pygame
from settings import *

# Change between screens
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
        self.state_history = []
        self.states = {}

    def add_state(self, name, state_obj):
        # Add a new state to the manager
        self.states[name] = state_obj

    def get_state(self):
        return self.states.get(self.currentState, None)
    
    def set_state(self, new_state):
        if self.currentState:
            self.state_history.append(self.currentState)
        self.currentState = new_state

    def get_previous_state(self):
        # If history is available, return the previous one. Return None if none exists
        if self.state_history:
            return self.state_history[-1]
        return None
    
    def go_back(self):
        # Pop the last state if available
        if self.state_history:
            self.currentState = self.state_history.pop()

    def all_states(self):
        return list(self.states.keys())
