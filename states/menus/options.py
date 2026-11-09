import pygame

from globals import (
    BUTTON_FONT_SIZE,
    FONT_PATH,
    GRAY,
    LIGHT_GRAY,
    MENU_BACKGROUND_COLOR,
    OVERLAY_ALPHA,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)
from systems import settings, sound
from systems.display import create_window
from ui_objects.slider import Slider
from ui_objects.text_button import TextButton
from ui_objects.text_label import TextLabel

TITLE_FONT_SIZE = 96
LABEL_FONT_SIZE = 24
TITLE_Y = 50
NAVIGATION_BUTTON_MARGIN = 20
FPS_BUTTON_Y = 220
FULL_SCREEN_BUTTON_Y = 300

SLIDER_WIDTH = 300
SLIDER_HEIGHT = 20
SLIDER_X = SCREEN_WIDTH // 2
SFX_SLIDER_Y = 475
MUSIC_SLIDER_Y = 575
SLIDER_LABEL_X = SLIDER_X - SLIDER_WIDTH // 2
SLIDER_LABEL_OFFSET_Y = 45

FPS_LABEL = "FPS: {}"
FULL_SCREEN_LABEL = "Fullscreen: {}"
MUSIC_LABEL = "Music Volume: {}"
SFX_LABEL = "SFX Volume: {}"


def _on_off(enabled):
    return "On" if enabled else "Off"


class Options:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

        self.title_font = pygame.font.Font(FONT_PATH, TITLE_FONT_SIZE)
        self.button_font = pygame.font.Font(FONT_PATH, BUTTON_FONT_SIZE)
        self.label_font = pygame.font.Font(FONT_PATH, LABEL_FONT_SIZE)
        self.title_image = self.title_font.render("OPTIONS", False, WHITE)
        self.title_pos = ((SCREEN_WIDTH - self.title_image.get_width()) // 2, TITLE_Y)

        # Slider math: Convert 0.0-1.0 float to 0-100 integer for UI display
        self.music_slider_value = int(settings.get_setting("music_volume") * 100)
        self.sfx_slider_value = int(settings.get_setting("sfx_volume") * 100)

        # Volume sliders and labels
        self.music_volume_slider = Slider(
            pos=(SLIDER_X, MUSIC_SLIDER_Y),
            size=(SLIDER_WIDTH, SLIDER_HEIGHT),
            initial_value=float(self.music_slider_value),
            min_value=0.0,
            max_value=100.0,
            track_color=WHITE,
            knob_color=LIGHT_GRAY,
        )
        self.music_volume_text = TextLabel(
            MUSIC_LABEL.format(self.music_slider_value),
            pos=(SLIDER_LABEL_X, MUSIC_SLIDER_Y - SLIDER_LABEL_OFFSET_Y),
            color=WHITE,
            font=self.label_font,
        )

        self.sfx_volume_slider = Slider(
            pos=(SLIDER_X, SFX_SLIDER_Y),
            size=(SLIDER_WIDTH, SLIDER_HEIGHT),
            initial_value=float(self.sfx_slider_value),
            min_value=0.0,
            max_value=100.0,
            track_color=WHITE,
            knob_color=LIGHT_GRAY,
        )
        self.sfx_volume_text = TextLabel(
            SFX_LABEL.format(self.sfx_slider_value),
            pos=(SLIDER_LABEL_X, SFX_SLIDER_Y - SLIDER_LABEL_OFFSET_Y),
            color=WHITE,
            font=self.label_font,
        )

        # Navigation Buttons
        self.main_menu_button = TextButton(
            "Main Menu",
            self.button_font,
            outline_color=GRAY,
        )
        self.main_menu_button.rect.bottomleft = (
            NAVIGATION_BUTTON_MARGIN,
            SCREEN_HEIGHT - NAVIGATION_BUTTON_MARGIN,
        )
        self.back_button = TextButton(
            "Back",
            self.button_font,
            outline_color=GRAY,
        )
        self.back_button.rect.bottomright = (
            SCREEN_WIDTH - NAVIGATION_BUTTON_MARGIN,
            SCREEN_HEIGHT - NAVIGATION_BUTTON_MARGIN,
        )

        # Toggle Buttons
        self.fps_button = TextButton(
            FPS_LABEL.format(_on_off(settings.get_setting("fps_enabled"))),
            self.button_font,
            (SCREEN_WIDTH // 2, FPS_BUTTON_Y),
            outline_color=GRAY,
        )

        self.full_screen_button = TextButton(
            FULL_SCREEN_LABEL.format(
                _on_off(settings.get_setting("full_screen_enabled"))
            ),
            self.button_font,
            (SCREEN_WIDTH // 2, FULL_SCREEN_BUTTON_Y),
            outline_color=GRAY,
        )

        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, OVERLAY_ALPHA))

    def can_go_back(self):
        return self.game_state_manager.get_previous_state() == "level"

    def draw(self, screen):
        if self.can_go_back():
            self.game_state_manager.states["level"].draw(screen)
            screen.blit(self.overlay, (0, 0))
        else:
            screen.fill(MENU_BACKGROUND_COLOR)

        screen.blit(self.title_image, self.title_pos)

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
            self.game_state_manager.set_state("main_menu")
            settings.save_settings()

        # Settings Toggles
        if self.fps_button.is_clicked():
            fps_enabled = not settings.get_setting("fps_enabled")
            settings.set_setting("fps_enabled", fps_enabled)
            self.fps_button.set_text(FPS_LABEL.format(_on_off(fps_enabled)))

        if self.full_screen_button.is_clicked():
            fullscreen = not settings.get_setting("full_screen_enabled")
            settings.set_setting("full_screen_enabled", fullscreen)
            self.full_screen_button.set_text(
                FULL_SCREEN_LABEL.format(_on_off(fullscreen))
            )
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
