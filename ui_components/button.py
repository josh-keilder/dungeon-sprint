import pygame

from globals import PALETTE_STEEL
from systems import sound
from ui_components.create_outline import draw_outline, make_outline


class Button:
    def __init__(
        self, image, pos=(0, 0), outline_color=PALETTE_STEEL, hover_image=None
    ):
        self.image = image
        self.hover_image = hover_image
        self.outline_color = outline_color
        self.outline = make_outline(self.image, self.outline_color)
        self.rect = self.image.get_frect()
        self.rect.topleft = pos
        self.hovered = False
        self.clicked_this_frame = False

    def draw(self, screen):
        # A hover image replaces the normal one; without one, hover draws an outline
        if self.hovered and self.hover_image is not None:
            screen.blit(self.hover_image, (self.rect.x, self.rect.y))
            return

        if self.hovered:
            draw_outline(screen, self.outline, (self.rect.x, self.rect.y))

        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if not self.hovered:
                sound.play_sfx("button_hover")
                self.hovered = True
        else:
            self.hovered = False

        self.clicked_this_frame = self.hovered and pygame.mouse.get_just_pressed()[0]

        if self.clicked_this_frame:
            sound.play_sfx("button_click")

    def is_clicked(self):
        return self.clicked_this_frame

    def set_image(self, image, hover_image=None):
        self.image = image
        self.hover_image = hover_image
        self.outline = make_outline(image, self.outline_color)
        self.rect = image.get_frect(topleft=self.rect.topleft)
