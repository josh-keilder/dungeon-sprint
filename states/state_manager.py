class GameStateManager:
    def __init__(self, start_state):
        self.states = {}
        self.current = start_state
        self.previous = None

    def add_state(self, name, state):
        self.states[name] = state

    def get_state(self):
        return self.states[self.current]

    def set_state(self, name):
        if name not in self.states:
            raise ValueError(f"Unknown state: {name}")

        self.previous = self.current
        self.current = name

    def get_previous_state(self):
        return self.previous

    def go_back(self):
        if self.previous is not None:
            self.set_state(self.previous)
