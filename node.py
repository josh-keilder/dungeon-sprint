class Node:
    def __init__(self):
        self.children = []
        self.parent = None
        self.active = True

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def update(self, dt=0):
        if not self.active:
            return
        for child in self.children:
            child.update(dt)
        
    def draw(self, screen, camera=None):
        if not self.active:
            return
        for child in self.children:
            child.draw(screen, camera)