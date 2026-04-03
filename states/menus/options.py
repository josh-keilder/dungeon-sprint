"""
State: Options Menu
-------------------
Handles the game settings interface. This state manages all settings. It acts as a bridge
between the UI components (Sliders/Buttons) and the persistent
SettingsManager/SoundController.

Classes:
    Options: The state object for adjusting game configurations.
"""

import pygame
from globals import *
from ui_objects.button import Button
from settings_manager import SettingsManager
from Controllers.sound import SoundController
from ui_objects.slider import Slider
from ui_objects.text_loader import Text_Loader
from ui_objects.camera import toggle_fullscreen
from typing import Any, Tuple, Optional


class Options:
    def __init__(
        self, screen: pygame.Surface, game_state_manager: Any, cursor: Any
    ) -> None:
        """
        Initializes settings UI elements and loads current values
        from the SettingsManager.

        Args:
            screen (pygame.Surface): The main display surface for rendering.
            game_state_manager (GameStateManager): The manager handling state transitions.
            cursor (Cursor): The custom cursor instance for visual feedback.

        Returns:
            None
        """
        self.screen = screen
        self.gameStateManager = game_state_manager
        self.cursor = cursor
        self.image = OPTIONS_SCREEN_IMAGE.convert_alpha()

        self.settings_manager = SettingsManager()
        self.sound_controller = SoundController()

        # Load current preferences from disk/memory
        self.fps_toggle = self.settings_manager.get("fps_enabled")
        self.bg_music_toggle = self.settings_manager.get("bg_music_enabled")
        self.full_screen_toggle = self.settings_manager.get("full_screen_enabled")

        # Slider math: Convert 0.0-1.0 float to 0-100 integer for UI display
        self.bg_music_volume = int(self.settings_manager.get("bg_music_volume") * 100)
        self.menu_sfx_volume = int(self.settings_manager.get("menu_sfx_volume") * 100)

        # UI Components: Volume Controls
        self.bg_music_volume_slider = Slider(
            self.screen,
            pos=(640, 575),
            size=(300, 20),
            initial_value=float(self.bg_music_volume),
            min_val=0.0,
            max_val=100.0,
            track_color=OPTION_MENU_BUTTON_BG,
            knob_color=LIGHT_GRAY,
        )
        self.bg_music_volume_text = Text_Loader(
            f"Music Volume: {self.bg_music_volume}",
            self.screen,
            pos=(500, 515),
            color=OPTION_MENU_BUTTON_BG,
        )

        self.menu_sfx_volume_slider = Slider(
            self.screen,
            pos=(640, 475),
            size=(300, 20),
            initial_value=float(self.menu_sfx_volume),
            min_val=0.0,
            max_val=100.0,
            track_color=OPTION_MENU_BUTTON_BG,
            knob_color=LIGHT_GRAY,
        )
        self.menu_sfx_volume_text = Text_Loader(
            f"Menu SFX Volume: {self.menu_sfx_volume}",
            self.screen,
            pos=(500, 415),
            color=OPTION_MENU_BUTTON_BG,
        )

        # Navigation Buttons
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

        # Toggle Buttons (FPS and placeholders for others)
        self.fps_button_off_img = pygame.transform.scale_by(
            FPS_BUTTON_OFF_IMAGE.convert_alpha(), 0.5
        )
        self.fps_button_on_img = pygame.transform.scale_by(
            FPS_BUTTON_ON_IMAGE.convert_alpha(), 0.5
        )

        initial_fps_img = (
            self.fps_button_on_img if self.fps_toggle else self.fps_button_off_img
        )
        self.fps_button = Button(self.screen, initial_fps_img, pos=(450, 200))

        self.bg_music_button = Button(self.screen, TEMP_BUTTON_IMAGE, pos=(450, 300))
        self.full_screen_button = Button(self.screen, TEMP_BUTTON_IMAGE, pos=(100, 300))

    def draw(self) -> None:
        """
        Renders all settings UI components to the active screen.

        Args:
            None

        Returns:
            None
        """
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

            # Only show 'Back' if we have a gameplay state to return to
            prev_state = self.gameStateManager.get_previous_state()
            if prev_state and prev_state.startswith("dungeon"):
                self.back_button.draw()

    def update(self, dt: float) -> None:
        """
        Processes settings changes and handles state navigation logic.

        Args:
            dt (float): Delta time in seconds since the last frame.

        Returns:
            None
        """
        self.main_menu_button.update()
        self.fps_button.update()
        self.full_screen_button.update()
        self.bg_music_button.update()
        self.bg_music_volume_slider.update()
        self.menu_sfx_volume_slider.update()

        # State Navigation
        if self.main_menu_button.is_clicked():
            self.gameStateManager.set_state("start")

        # Settings Toggles
        if self.fps_button.is_clicked():
            self.fps_toggle = not self.fps_toggle
            self.settings_manager.set("fps_enabled", self.fps_toggle)
            self.fps_button.image = (
                self.fps_button_on_img if self.fps_toggle else self.fps_button_off_img
            )

        if self.full_screen_button.is_clicked():
            self.full_screen_toggle = not self.full_screen_toggle
            new_screen = toggle_fullscreen()
            self.screen = new_screen
            self.gameStateManager.update_screen_reference(new_screen)
            self.cursor.screen = new_screen

        if self.bg_music_button.is_clicked():
            self.bg_music_toggle = not self.bg_music_toggle
            self.settings_manager.set("bg_music_enabled", self.bg_music_toggle)
            if self.bg_music_toggle:
                self.sound_controller.play_music()
            else:
                self.sound_controller.stop_music()

        # Volume Slider Logic
        new_bg_vol = self.bg_music_volume_slider.get_current_value()
        if new_bg_vol != self.bg_music_volume:
            self.bg_music_volume = new_bg_vol
            self.bg_music_volume_text.update_text(
                f"Music Volume: {self.bg_music_volume}"
            )
            self.sound_controller.set_music_volume(self.bg_music_volume / 100.0)
            self.settings_manager.set("bg_music_volume", self.bg_music_volume / 100.0)

        new_sfx_vol = self.menu_sfx_volume_slider.get_current_value()
        if new_sfx_vol != self.menu_sfx_volume:
            self.menu_sfx_volume = new_sfx_vol
            self.menu_sfx_volume_text.update_text(
                f"Menu SFX Volume: {self.menu_sfx_volume}"
            )
            self.sound_controller.set_menu_sfx_volume(self.menu_sfx_volume / 100.0)
            self.settings_manager.set("menu_sfx_volume", self.menu_sfx_volume / 100.0)

        # Contextual Back Logic
        prev_state = self.gameStateManager.get_previous_state()
        if prev_state and prev_state.startswith("dungeon"):
            self.back_button.update()
            if self.back_button.is_clicked():
                self.gameStateManager.go_back()
