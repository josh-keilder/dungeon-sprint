from Controllers.animations import AnimationController
from Components.component import Component

class AnimationComponent(Component):
    def __init__(self, node, animations, start_anim):
        super().__init__(node)
        self.controller = AnimationController(animations=animations, start_anim=start_anim)

    def update(self, dt=0):
        if hasattr(self.node, 'walking') and hasattr(self.node, 'last_direction'):
            if self.node.walking and not getattr(self.node.roll, 'is_rolling', False):
                self.controller.set_animation(f'player_walk_{self.node.last_direction}')
            elif not getattr(self.node.roll, 'is_rolling', False):
                self.controller.set_animation(f'player_idle_{self.node.last_direction}')
        
        self.node.image = self.controller.play_animation(loop=True)