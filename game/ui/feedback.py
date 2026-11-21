from engine.core import settings
from engine.graphics.particles import emit_burst
from engine.graphics.shake import new_shake, start_shake, update_shake
from engine.io import sound
from game.data.particle_presets import CRATE_DEBRIS
from game.ui.hurt_vignette import HurtVignette

# Shake strengths, in world pixels
HIT_SHAKE_STRENGTH = 1  # the player's roll hits an enemy
HURT_SHAKE_STRENGTH = 4  # the player is hurt


class Feedback:
    # What the player sees and hears when something happens: each frame's events, from
    # the player, combat and the floor, become sounds, particles, camera shake and the
    # hurt vignette. The shake and the vignette only play if their setting is on.
    def __init__(self):
        self.shake = new_shake()
        self.hurt_vignette = HurtVignette()

    def update(self, dt):
        update_shake(self.shake, dt)
        self.hurt_vignette.update(dt)

    def draw(self, screen):
        self.hurt_vignette.draw(screen)

    def handle(self, events, particles):
        for event in events:
            name = event["name"]
            if name == "healed":
                sound.play_sfx("heal")
            elif name == "roll_hit":
                enemy = event["enemy"]
                sound.play_sfx("roll_hit")
                emit_burst(
                    particles,
                    enemy.rect.center,
                    enemy.hit_particles,
                    enemy.knockback_velocity,
                )
                self.shake_camera(HIT_SHAKE_STRENGTH)
            elif name == "player_hurt":
                self.shake_camera(HURT_SHAKE_STRENGTH)
                if settings.get_setting("hurt_vignette_enabled"):
                    self.hurt_vignette.start()
            elif name == "crate_broken":
                emit_burst(particles, event["crate"].rect.center, CRATE_DEBRIS)

    def camera_offset(self):
        return self.shake["offset"]

    def shake_camera(self, strength):
        if settings.get_setting("screen_shake_enabled"):
            start_shake(self.shake, strength)
