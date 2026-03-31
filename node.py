class Node:
    def __init__(self):
        self.children = []
        self.parent = None
        self.active = True
        self.z_index = 0 

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        # Safety check: ensure the child is actually in the list
        if child in self.children:
            self.children.remove(child)

    def update(self, dt=0):
        if not self.active:
            return
        
        for child in self.children[:]:
            child.update(dt)
        
    def draw(self, screen, camera=None):
        if not self.active:
            return

        self.children.sort(key=lambda c: getattr(c, 'rect', getattr(c, 'pos', [0, 0]))[1] if hasattr(c, 'rect') or hasattr(c, 'pos') else 0)

        for child in self.children:
            if camera and hasattr(child, 'rect'):
                if not camera.colliderect(child.rect):
                    continue
                    
            child.draw(screen, camera)