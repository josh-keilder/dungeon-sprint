from engine.core.timer import (
    advance_timer,
    is_running,
    new_timer,
    start_timer,
    time_elapsed,
)
from engine.io import sound

# Death: the world freezes while the player's body fades, then the game-over screen
DEATH_DELAY = 3.0  # seconds, the whole freeze
DEATH_FADE_DURATION = 1.5  # seconds; must be no longer than DEATH_DELAY


class DeathSequence:
    def __init__(self):
        self.active = False
        self.timer = new_timer()

    def start(self):
        self.active = True
        start_timer(self.timer, DEATH_DELAY)
        sound.stop_music()
        sound.play_sfx("death")

    def is_active(self):
        return self.active

    def update(self, dt, player):
        # Fades the player's body out; True once the freeze is over
        advance_timer(self.timer, dt)
        fade_progress = min(1.0, time_elapsed(self.timer) / DEATH_FADE_DURATION)
        player.alpha = round(255 * (1 - fade_progress))
        return not is_running(self.timer)
