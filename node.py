"""
Core Scene-Graph Component: Node
--------------------------------
Provides a base class for hierarchical object management. Each Node can
contain children, allowing for nested updates and Y-sorted rendering.

Attributes:
    children (list): A list of child Node instances.
    parent (Node): Reference to the parent Node, if any.
    active (bool): Flag to toggle updates and drawing for the node and its subtree.
    z_index (int): Manual layering depth (can be used for custom sorting).
"""


class Node:
    def __init__(self):
        self.children = []
        self.parent = None
        self.active = True
        self.z_index = 0

    def add_child(self, child):
        """Assigns this node as the parent and adds the child to the hierarchy."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        """Safely removes a child from the hierarchy."""
        if child in self.children:
            self.children.remove(child)

    def update(self, dt=0):
        """Recursively updates all active children."""
        if not self.active:
            return

        # Slicing the list [:] allows safe removal of children during the loop
        for child in self.children[:]:
            child.update(dt)

    def draw(self, screen, camera=None):
        """
        Sorts children by their Y-position for depth perception and renders
        them if they are within the camera view.
        """
        if not self.active:
            return

        # Depth Sorting: Sorts based on the 'y' coordinate of 'rect' or 'pos'
        self.children.sort(
            key=lambda c: (
                getattr(c, "rect", getattr(c, "pos", [0, 0]))[1]
                if hasattr(c, "rect") or hasattr(c, "pos")
                else 0
            )
        )

        for child in self.children:
            # Frustum Culling: Skip drawing if the child has a rect and is off-screen
            if camera and hasattr(child, "rect"):
                if not camera.colliderect(child.rect):
                    continue

            child.draw(screen, camera)
