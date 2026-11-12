import pygame

from globals import FONT_PATH, GAME_SCALE, PALETTE_STEEL


class TextLabel:
    def __init__(
        self,
        text,
        font_size=24,
        color=PALETTE_STEEL,
        pos=(0, 0),
        font=None,
        outline_color=None,
    ):
        pygame.font.init()

        if font is None:
            self.font = pygame.font.Font(FONT_PATH, font_size)
        else:
            self.font = font

        self.color = color
        self.outline_color = outline_color
        self.pos = pos

        self.text = None
        self.update_text(text)

    def draw(self, screen):
        if self.outline_surface is not None:
            for offset_x, offset_y in (
                (-GAME_SCALE, 0),
                (GAME_SCALE, 0),
                (0, -GAME_SCALE),
                (0, GAME_SCALE),
            ):
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
