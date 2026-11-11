from globals import PALETTE_STEEL, PALETTE_TORCH
from ui_components.button import Button


class TextButton(Button):
    def __init__(
        self,
        text,
        font,
        midtop=(0, 0),
        text_color=PALETTE_STEEL,
        hover_color=PALETTE_TORCH,
    ):
        self.font = font
        self.text_color = text_color
        self.hover_color = hover_color
        image = self.font.render(text, False, self.text_color)
        hover_image = self.font.render(text, False, self.hover_color)

        super().__init__(image, hover_image=hover_image)

        self.rect.midtop = midtop

    def set_text(self, text):
        midtop = self.rect.midtop
        image = self.font.render(text, False, self.text_color)
        hover_image = self.font.render(text, False, self.hover_color)
        self.set_image(image, hover_image)
        self.rect.midtop = midtop
