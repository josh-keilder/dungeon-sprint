from engine.ui.button import Button
from engine.ui.theme import get_theme


class TextButton(Button):
    def __init__(
        self,
        text,
        font,
        midtop=(0, 0),
        text_color=None,
        hover_color=None,
    ):
        if text_color is None:
            text_color = get_theme("text_color")
        if hover_color is None:
            hover_color = get_theme("hover_color")

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
