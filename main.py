import pygame

from engine.core import settings
from engine.core.assets import load_image
from engine.core.game_loop import GameLoop
from engine.core.state_manager import GameStateManager
from engine.graphics.display import create_window
from engine.graphics.renderer import Renderer
from engine.io import sound
from engine.ui.theme import set_theme
from game.data.constants import (
    DEFAULT_SETTINGS,
    FONT_PATH,
    FRAME_RATE,
    GAME_SCALE,
    MUSIC_FOLDER,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SETTINGS_FILE_PATH,
    SFX_FOLDER,
    TILE_SIZE,
    WINDOW_TITLE,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from game.data.light_types import AMBIENT_LIGHT, LIGHT_BANDS, MAX_LIGHT
from game.data.palette import (
    GREEN,
    PALETTE_BLOOD,
    PALETTE_SHADOW,
    PALETTE_STEEL,
    PALETTE_TORCH,
    PALETTE_VOID,
    RED,
)
from game.states.menus.main_menu import MainMenu
from game.states.menus.options import OptionsMenu
from game.states.menus.run_end import RunEndScreen
from game.states.run import Run

# Cursor art
CURSOR_IMAGE_PATH = "Assets/Cursors/01.png"

# Music for the death screen (the finish screen keeps the level music)
GAME_OVER_MUSIC = "game_over"


def main():
    pygame.init()
    settings.load_settings(DEFAULT_SETTINGS, SETTINGS_FILE_PATH)

    # The theme first: every screen and widget reads it when it's built
    apply_theme()

    create_window(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        settings.get_setting("full_screen_enabled"),
        WINDOW_TITLE,
    )
    renderer = make_renderer()
    load_sound()

    cursor_image = pygame.transform.scale_by(load_image(CURSOR_IMAGE_PATH), 0.5)
    game_loop = GameLoop(
        renderer,
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        build_screens(),
        FRAME_RATE,
        cursor_image=cursor_image,
        fps_setting="fps_enabled",
    )
    game_loop.run()
    pygame.quit()


def apply_theme():
    # The look every engine widget reads
    set_theme(
        font_path=FONT_PATH,
        font_size=24,  # Silkscreen at 24 sits on the 3x pixel grid
        pixel_scale=GAME_SCALE,
        text_color=PALETTE_STEEL,
        text_outline_color=PALETTE_VOID,
        hover_color=PALETTE_TORCH,
        button_outline_color=PALETTE_STEEL,
        slider_empty_color=PALETTE_SHADOW,
        hover_sound="button_hover",
        click_sound="button_click",
        health_bar_border_color=PALETTE_VOID,
        health_bar_empty_color=PALETTE_SHADOW,
        health_bar_fill_color=PALETTE_BLOOD,
    )


def make_renderer():
    return Renderer(
        screen_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        world_size=(WORLD_WIDTH, WORLD_HEIGHT),
        world_scale=GAME_SCALE,
        tile_size=TILE_SIZE,
        lighting={
            "ambient": AMBIENT_LIGHT,
            "max_light": MAX_LIGHT,
            "bands": LIGHT_BANDS,
            "void_color": PALETTE_VOID,  # wall tiles' empty part never takes light
        },
    )


def load_sound():
    # Load the files, then apply the saved volumes
    sound.load_sfx(SFX_FOLDER)
    sound.load_music(MUSIC_FOLDER)
    sound.set_sfx_volume(settings.get_setting("sfx_volume"))
    sound.set_music_volume(settings.get_setting("music_volume"))


def build_screens():
    # Every screen, and the manager that switches between them
    game_state_manager = GameStateManager("main_menu")
    game_state_manager.add_state("main_menu", MainMenu(game_state_manager))
    game_state_manager.add_state("options", OptionsMenu(game_state_manager))
    game_state_manager.add_state("run", Run(game_state_manager))
    game_state_manager.add_state(
        "game_over",
        RunEndScreen(game_state_manager, "You Died!", RED, GAME_OVER_MUSIC),
    )
    game_state_manager.add_state(
        "run_complete",
        RunEndScreen(game_state_manager, "You Escaped!", GREEN, None),
    )
    return game_state_manager


if __name__ == "__main__":
    main()
