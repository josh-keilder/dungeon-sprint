from globals import WHITE
from ui_components.button import Button


class TextButton(Button):
    def __init__(
        self, text, font, midtop=(0, 0), text_color=WHITE, outline_color=WHITE
    ):
        self.font = font
        self.text_color = text_color
        image = self.font.render(text, False, self.text_color)

        super().__init__(image, outline_color=outline_color)

        self.rect.midtop = midtop

    def set_text(self, text):
        midtop = self.rect.midtop
        image = self.font.render(text, False, self.text_color)
        self.set_image(image)
        self.rect.midtop = midtop
