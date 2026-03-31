from Controllers.animations import AnimationController
from Components.component import Component


class AnimationComponent(Component):
    def __init__(self, node, animations, start_anim, anim_speed=10):
        super().__init__(node)
        self.anim_speed = anim_speed

        self.controller = AnimationController(
            animations=animations,
            start_anim=start_anim,
            animation_speed=self.anim_speed,
        )

    def change_anim(self, anim_name):
        self.controller.set_animation(anim_name)

    def update(self, dt):
        self.node.image = self.controller.play_animation(dt, loop=True)
