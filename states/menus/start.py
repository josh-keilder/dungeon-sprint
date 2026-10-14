import pygame

from systems.assets import load_image
from ui_objects.button import Button

START_SCREEN_PATH = "Assets/Menu-Assets/start-screen_1.png"
START_BUTTON_PATH = "Assets/Menu-Assets/start-button.png"
EXIT_BUTTON_PATH = "Assets/Menu-Assets/exit-button.png"
OPTIONS_BUTTON_PATH = "Assets/Menu-Assets/options-button.png"


class Start:
    def __init__(self, gameStateManager):
        self.gameStateManager = gameStateManager
        self.image = load_image(START_SCREEN_PATH)
        self.start_button_img = load_image(START_BUTTON_PATH)
        self.exit_button_img = load_image(EXIT_BUTTON_PATH)
        self.options_button_img = load_image(OPTIONS_BUTTON_PATH)

        self.start_button = Button(self.start_button_img, pos=(416, 288))
        self.exit_button = Button(self.exit_button_img, pos=(416, 448))
        self.options_button = Button(
            pygame.transform.scale_by(self.options_button_img, 0.5),
            pos=(985, 650),
        )

    def draw(self, screen):
        screen.blit(self.image, (0, 0))
        self.start_button.draw(screen)
        self.exit_button.draw(screen)
        self.options_button.draw(screen)

    def update(self, dt):
        self.start_button.update()
        self.exit_button.update()
        self.options_button.update()

        # Navigation Logic
        if self.start_button.is_clicked():
            self.gameStateManager.set_state("level")

        elif self.options_button.is_clicked():
            self.gameStateManager.set_state("options")

        elif self.exit_button.is_clicked():
            pygame.event.post(pygame.event.Event(pygame.QUIT))
