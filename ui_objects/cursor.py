import pygame


class Cursor:
    def __init__(self, image):
        self.image = image
        # Using frect (float rect) for sub-pixel precision and smoother movement
        self.rect = self.image.get_frect()

    def set_image(self, new_image):
        self.image = new_image
        self.rect = self.image.get_frect(center=self.rect.center)

    def update(self):
        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()

        # Draw the cursor image centered slightly down-right of the mouse
        self.rect.center = mouse_pos_x + 5, mouse_pos_y + 5

    def draw(self, screen):
        screen.blit(self.image, self.rect)
