from systems.display import get_mouse_pos

# Where the cursor image sits relative to the mouse
CURSOR_OFFSET = 5  # pixels down and to the right


class Cursor:
    def __init__(self, image):
        self.image = image
        # A float rect, for sub-pixel precision and smoother movement
        self.rect = self.image.get_frect()

    def update(self):
        mouse_pos_x, mouse_pos_y = get_mouse_pos()

        # Draw the cursor image centered slightly down-right of the mouse
        self.rect.center = mouse_pos_x + CURSOR_OFFSET, mouse_pos_y + CURSOR_OFFSET

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def set_image(self, new_image):
        self.image = new_image
        self.rect = self.image.get_frect(center=self.rect.center)
