from engine.core import settings
from engine.graphics.shake import new_shake, start_shake, update_shake
from game.ui.hurt_vignette import HurtVignette

# Shake strengths, in world pixels
HIT_SHAKE_STRENGTH = 1  # the player's roll hits an enemy
HURT_SHAKE_STRENGTH = 4  # the player is hurt


class HitFeedback:
    # How hits feel: a camera shake, and a red vignette when the player is hurt.
    # Each one only plays if its setting is on.
    def __init__(self):
        self.shake = new_shake()
        self.hurt_vignette = HurtVignette()

    def update(self, dt):
        update_shake(self.shake, dt)
        self.hurt_vignette.update(dt)

    def on_hit(self):
        self.shake_camera(HIT_SHAKE_STRENGTH)

    def on_hurt(self):
        self.shake_camera(HURT_SHAKE_STRENGTH)
        if settings.get_setting("hurt_vignette_enabled"):
            self.hurt_vignette.start()

    def shake_camera(self, strength):
        if settings.get_setting("screen_shake_enabled"):
            start_shake(self.shake, strength)

    def camera_offset(self):
        return self.shake["offset"]

    def draw(self, screen):
        self.hurt_vignette.draw(screen)
