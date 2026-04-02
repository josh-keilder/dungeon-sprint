import pygame
from globals import *
from ui_objects.button import Button
from settings_manager import SettingsManager
from Controllers.sound import SoundController
from ui_objects.slider import Slider
from ui_objects.text_loader import Text_Loader
from ui_objects.camera import toggle_fullscreen


class Options:
    def __init__(self, screen, gameStateManager, cursor):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.cursor = cursor
        self.image = OPTIONS_SCREEN_IMAGE.convert_alpha()

        self.settings_manager = SettingsManager()
        self.sound_controller = SoundController()

        # Settings
        self.fps_toggle = self.settings_manager.get("fps_enabled")
        self.bg_music_toggle = self.settings_manager.get("bg_music_enabled")
        self.full_screen_toggle = self.settings_manager.get("full_screen_enabled")

        self.bg_music_volume = (
            self.settings_manager.get("bg_music_volume") * 100
        )  # Multiply volume by 100 for the slider to work
        self.menu_sfx_volume = self.settings_manager.get("menu_sfx_volume") * 100

        # Sliders
        self.bg_music_volume_slider = Slider(
            self.screen,
            pos=(640, 575),
            size=(300, 20),
            initial_value=self.bg_music_volume,
            min_val=0,
            max_val=100,
            track_color=OPTION_MENU_BUTTON_BG,
            knob_color=LIGHT_GRAY,
        )
        self.bg_music_volume_text = Text_Loader(
            f"Music Volume: {int(self.bg_music_volume)}",
            self.screen,
            pos=(500, 515),
            color=OPTION_MENU_BUTTON_BG,
        )
        self.menu_sfx_volume_slider = Slider(
            self.screen,
            pos=(640, 475),  # Adjusted Y pos to be above the music slider
            size=(300, 20),
            initial_value=self.menu_sfx_volume,
            min_val=0,
            max_val=100,
            track_color=OPTION_MENU_BUTTON_BG,
            knob_color=LIGHT_GRAY,
        )
        self.menu_sfx_volume_text = Text_Loader(
            f"Menu SFX Volume: {int(self.menu_sfx_volume)}",
            self.screen,
            pos=(500, 415),
            color=OPTION_MENU_BUTTON_BG,
        )

        # Option menu buttons
        self.main_menu_button_img = MAIN_MENU_BUTTON_IMAGE.convert_alpha()
        self.main_menu_button = Button(
            self.screen,
            pygame.transform.scale_by(self.main_menu_button_img, 0.4),
            pos=(15, 650),
        )
        self.back_button_img = BACK_BUTTON_IMAGE.convert_alpha()
        self.back_button = Button(
            self.screen,
            pygame.transform.scale_by(self.back_button_img, 0.4),
            pos=(1135, 650),
        )

        self.fps_button_off_img = pygame.transform.scale_by(
            FPS_BUTTON_OFF_IMAGE.convert_alpha(), 0.5
        )
        self.fps_button_on_img = pygame.transform.scale_by(
            FPS_BUTTON_ON_IMAGE.convert_alpha(), 0.5
        )
        initial_fps_button_img = (
            self.fps_button_on_img if self.fps_toggle else self.fps_button_off_img
        )
        self.fps_button = Button(self.screen, initial_fps_button_img, pos=(450, 200))

        self.bg_music_button_off_img = TEMP_BUTTON_IMAGE
        self.bg_music_button_on_img = TEMP_BUTTON_IMAGE
        self.bg_music_button = Button(self.screen, TEMP_BUTTON_IMAGE, pos=(450, 300))

        self.full_screen_button_off_img = TEMP_BUTTON_IMAGE
        self.full_screen_button_on_img = TEMP_BUTTON_IMAGE
        self.full_screen_button = Button(self.screen, TEMP_BUTTON_IMAGE, pos=(100, 300))

    def draw(self):
        self.screen.blit(self.image, (0, 0))

        if self.gameStateManager.currentState == "options":
            self.main_menu_button.draw()
            self.full_screen_button.draw()
            self.fps_button.draw()
            self.bg_music_button.draw()

            self.bg_music_volume_slider.draw()
            self.bg_music_volume_text.draw()

            self.menu_sfx_volume_slider.draw()
            self.menu_sfx_volume_text.draw()

            if self.gameStateManager.get_previous_state().startswith("dungeon"):
                self.back_button.draw()

    def update(self, dt):
        self.main_menu_button.update()
        self.fps_button.update()
        self.full_screen_button.update()
        self.bg_music_button.update()

        self.bg_music_volume_slider.update()
        self.menu_sfx_volume_slider.update()

        if self.main_menu_button.is_clicked():
            self.gameStateManager.set_state("start")

        if self.fps_button.is_clicked():
            self.fps_toggle = not self.fps_toggle

            self.settings_manager.set("fps_enabled", self.fps_toggle)

            if self.fps_toggle == True:
                self.fps_button.image = self.fps_button_on_img
            else:
                self.fps_button.image = self.fps_button_off_img

        if self.full_screen_button.is_clicked():
            self.full_screen_toggle = not self.full_screen_toggle

            new_screen = toggle_fullscreen()

            self.screen = new_screen

            self.gameStateManager.update_screen_reference(new_screen)
            self.cursor.screen = new_screen

            if self.full_screen_toggle == True:
                self.full_screen_button.image = self.full_screen_button_on_img
            else:
                self.full_screen_button.image = self.full_screen_button_off_img

        if self.bg_music_button.is_clicked():
            self.bg_music_toggle = not self.bg_music_toggle

            self.settings_manager.set("bg_music_enabled", self.bg_music_toggle)
            if self.bg_music_toggle == True:
                self.bg_music_button.image = self.bg_music_button_on_img
                self.sound_controller.play_music()
            else:
                self.sound_controller.stop_music()
                self.bg_music_button.image = self.bg_music_button_off_img

        # Update Music Slider
        new_bg_volume_val_int = self.bg_music_volume_slider.get_current_value()
        if new_bg_volume_val_int != self.bg_music_volume:
            self.bg_music_volume = new_bg_volume_val_int

            self.bg_music_volume_text.update_text(
                f"Music Volume: {self.bg_music_volume}"
            )

            normalized_vol = self.bg_music_volume / 100.0
            self.sound_controller.set_music_volume(normalized_vol)

            self.settings_manager.set("bg_music_volume", normalized_vol)

        # Update SFX Slider
        self.menu_sfx_volume_slider.update()
        new_menu_sfx_val = self.menu_sfx_volume_slider.get_current_value()

        if new_menu_sfx_val != self.menu_sfx_volume:
            self.menu_sfx_volume = new_menu_sfx_val
            self.menu_sfx_volume_text.update_text(
                f"Menu SFX Volume: {self.menu_sfx_volume}"
            )

            normalized_sfx = self.menu_sfx_volume / 100.0
            self.sound_controller.set_menu_sfx_volume(normalized_sfx)
            self.settings_manager.set("menu_sfx_volume", normalized_sfx)

        if self.gameStateManager.get_previous_state().startswith("dungeon"):
            self.back_button.update()
            if self.back_button.is_clicked():
                self.gameStateManager.go_back()
