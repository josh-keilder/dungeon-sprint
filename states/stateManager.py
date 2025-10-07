import pygame
from settings import *

# Change between screens
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
        self.state_history = []
    def get_state(self):
        return self.currentState
    def set_state(self, new_state):
        if self.currentState:
            self.state_history.append(self.currentState)
        self.currentState = new_state
    def get_previous_state(self):
        # If history is available, return the previous one
        if self.state_history:
            return self.state_history[-1]
        return None
    def go_back(self):
        # Pop the last state if available
        if self.state_history:
            self.currentState = self.state_history.pop()