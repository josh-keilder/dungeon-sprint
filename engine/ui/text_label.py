import pygame

from engine.ui.theme import get_theme


class TextLabel:
    def __init__(
        self,
        text,
        font_size=None,
        color=None,
        pos=(0, 0),
        font=None,
        outline_color=None,
    ):
        pygame.font.init()

        if font is None:
            if font_size is None:
                font_size = get_theme("font_size")
            self.font = pygame.font.Font(get_theme("font_path"), font_size)
        else:
            self.font = font

        if color is None:
            color = get_theme("text_color")
        self.color = color
        self.outline_color = outline_color
        self.pos = pos

        # The shown text; None makes update_text render the first one
        self.text = None
        self.update_text(text)

    def draw(self, screen):
        if self.outline_surface is not None:
            # The outline color drawn one pixel-grid step away in 4 directions
            step = get_theme("pixel_scale")
            for offset_x, offset_y in ((-step, 0), (step, 0), (0, -step), (0, step)):
                screen.blit(
                    self.outline_surface,
                    (self.pos[0] + offset_x, self.pos[1] + offset_y),
                )

        screen.blit(self.text_surface, self.pos)

    def update_text(self, new_text):
        new_text = str(new_text)

        if new_text == self.text:
            return

        self.text = new_text

        # False means no anti-aliasing, for a crisper pixel look
        self.text_surface = self.font.render(new_text, False, self.color)

        self.outline_surface = None

        if self.outline_color is not None:
            self.outline_surface = self.font.render(new_text, False, self.outline_color)
