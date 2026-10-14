import pygame

from globals import BLACK


class TextLabel:
    def __init__(
        self,
        text,
        font_name="Comic Sans MS",
        font_size=30,
        color=BLACK,
        pos=(0, 0),
    ):
        pygame.font.init()
        self.font = pygame.font.SysFont(font_name, font_size)
        self.color = color
        self.pos = pos

        # Initial render: False indicates no anti-aliasing for a crisper pixel look
        self.text_surface = self.font.render(str(text), False, self.color)

    def draw(self, screen):
        screen.blit(self.text_surface, self.pos)

    def update_text(self, new_text):
        self.text_surface = self.font.render(str(new_text), False, self.color)
