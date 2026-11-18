from engine.ui.text_label import TextLabel
from engine.ui.text_layout import centered_text_y
from engine.ui.theme import get_theme

# Placement: top right, right-aligned by ink so a wider number grows to the left
FPS_MARGIN = 12  # pixels from the right edge
FPS_CENTER_Y = 21  # pixels from the top

# Refreshing every frame would make the number unreadable
FPS_REFRESH_INTERVAL = 0.5  # seconds


class FpsCounter:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.refresh_timer = 0.0
        self.label = TextLabel("", outline_color=get_theme("text_outline_color"))

    def update(self, dt, fps):
        self.refresh_timer += dt
        if self.refresh_timer < FPS_REFRESH_INTERVAL:
            return

        self.refresh_timer -= FPS_REFRESH_INTERVAL
        self.label.update_text(f"FPS: {int(fps)}")

        ink = self.label.text_surface.get_bounding_rect()
        self.label.pos = (
            self.screen_width - FPS_MARGIN - ink.right,
            centered_text_y(self.label.text_surface, FPS_CENTER_Y),
        )

    def draw(self, screen):
        self.label.draw(screen)
