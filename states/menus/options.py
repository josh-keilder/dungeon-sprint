import pygame

from globals import (
    LIGHT_GRAY,
    OPTION_MENU_BUTTON_BACKGROUND,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from systems import settings, sound
from systems.assets import load_image
from systems.display import create_window
from ui_objects.button import Button
from ui_objects.slider import Slider
from ui_objects.text_label import TextLabel

OPTIONS_SCREEN_PATH = "Assets/Menu-Assets/options-screen.png"
MAIN_MENU_BUTTON_PATH = "Assets/Menu-Assets/main-menu-button.png"
BACK_BUTTON_PATH = "Assets/Menu-Assets/back-button.png"
FPS_ON_PATH = "Assets/Menu-Assets/Fps_On.png"
FPS_OFF_PATH = "Assets/Menu-Assets/Fps_Off.png"
TEMP_BUTTON_PATH = "Assets/Menu-Assets/temp_button.png"

MUSIC_LABEL = "Music Volume: {}"
SFX_LABEL = "SFX Volume: {}"


class Options:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

        self.image = load_image(OPTIONS_SCREEN_PATH)

        # Slider math: Convert 0.0-1.0 float to 0-100 integer for UI display
        self.music_slider_value = int(settings.get_setting("music_volume") * 100)
        self.sfx_slider_value = int(settings.get_setting("sfx_volume") * 100)

        # Volume sliders and labels
        self.music_volume_slider = Slider(
            pos=(640, 575),
            size=(300, 20),
            initial_value=float(self.music_slider_value),
            min_value=0.0,
            max_value=100.0,
            track_color=OPTION_MENU_BUTTON_BACKGROUND,
            knob_color=LIGHT_GRAY,
        )
        self.music_volume_text = TextLabel(
            MUSIC_LABEL.format(self.music_slider_value),
            pos=(500, 515),
            color=OPTION_MENU_BUTTON_BACKGROUND,
        )

        self.sfx_volume_slider = Slider(
            pos=(640, 475),
            size=(300, 20),
            initial_value=float(self.sfx_slider_value),
            min_value=0.0,
            max_value=100.0,
            track_color=OPTION_MENU_BUTTON_BACKGROUND,
            knob_color=LIGHT_GRAY,
        )
        self.sfx_volume_text = TextLabel(
            SFX_LABEL.format(self.sfx_slider_value),
            pos=(500, 415),
            color=OPTION_MENU_BUTTON_BACKGROUND,
        )

        # Navigation Buttons
        self.main_menu_button_image = load_image(MAIN_MENU_BUTTON_PATH)
        self.main_menu_button = Button(
            pygame.transform.scale_by(self.main_menu_button_image, 0.4),
            pos=(15, 650),
        )
        self.back_button_image = load_image(BACK_BUTTON_PATH)
        self.back_button = Button(
            pygame.transform.scale_by(self.back_button_image, 0.4),
            pos=(1135, 650),
        )

        # Toggle buttons: FPS and fullscreen
        self.fps_button_off_image = pygame.transform.scale_by(
            load_image(FPS_OFF_PATH), 0.5
        )
        self.fps_button_on_image = pygame.transform.scale_by(
            load_image(FPS_ON_PATH), 0.5
        )

        initial_fps_image = (
            self.fps_button_on_image
            if settings.get_setting("fps_enabled")
            else self.fps_button_off_image
        )
        self.fps_button = Button(initial_fps_image, pos=(450, 200))

        self.full_screen_button = Button(load_image(TEMP_BUTTON_PATH), pos=(100, 300))

    def can_go_back(self):
        return self.game_state_manager.get_previous_state() == "level"

    def draw(self, screen):
        screen.blit(self.image, (0, 0))

        self.main_menu_button.draw(screen)
        self.full_screen_button.draw(screen)
        self.fps_button.draw(screen)

        self.music_volume_slider.draw(screen)
        self.music_volume_text.draw(screen)

        self.sfx_volume_slider.draw(screen)
        self.sfx_volume_text.draw(screen)

        # Only show 'Back' if we have a gameplay state to return to
        if self.can_go_back():
            self.back_button.draw(screen)

    def update(self, dt):
        self.main_menu_button.update()
        self.fps_button.update()
        self.full_screen_button.update()
        self.music_volume_slider.update()
        self.sfx_volume_slider.update()

        # State Navigation
        if self.main_menu_button.is_clicked():
            self.game_state_manager.set_state("start")
            settings.save_settings()

        # Settings Toggles
        if self.fps_button.is_clicked():
            fps_enabled = not settings.get_setting("fps_enabled")
            settings.set_setting("fps_enabled", fps_enabled)
            self.fps_button.set_image(
                self.fps_button_on_image if fps_enabled else self.fps_button_off_image
            )

        if self.full_screen_button.is_clicked():
            fullscreen = not settings.get_setting("full_screen_enabled")
            settings.set_setting("full_screen_enabled", fullscreen)
            create_window(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen)

        # Apply a volume change when a slider moves
        new_music_value = self.music_volume_slider.get_current_value()
        if new_music_value != self.music_slider_value:
            self.music_slider_value = new_music_value
            self.music_volume_text.update_text(
                MUSIC_LABEL.format(self.music_slider_value)
            )
            sound.set_music_volume(self.music_slider_value / 100.0)
            settings.set_setting("music_volume", self.music_slider_value / 100.0)

        new_sfx_value = self.sfx_volume_slider.get_current_value()
        if new_sfx_value != self.sfx_slider_value:
            self.sfx_slider_value = new_sfx_value
            self.sfx_volume_text.update_text(SFX_LABEL.format(self.sfx_slider_value))
            sound.set_sfx_volume(self.sfx_slider_value / 100.0)
            settings.set_setting("sfx_volume", self.sfx_slider_value / 100.0)

        # Back button, only when we came from the level
        if self.can_go_back():
            self.back_button.update()
            if self.back_button.is_clicked():
                self.game_state_manager.go_back()
                settings.save_settings()
