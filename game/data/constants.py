import math

# Screen and timing
WINDOW_TITLE = "Dungeon Sprint"
SCREEN_WIDTH = 1280  # pixels
SCREEN_HEIGHT = 720  # pixels
FRAME_RATE = 240  # frames per second cap

# World canvas: the world is drawn at 1x, then scaled up by GAME_SCALE
GAME_SCALE = 3
WORLD_WIDTH = math.ceil(SCREEN_WIDTH / GAME_SCALE)  # 427 world pixels
WORLD_HEIGHT = math.ceil(SCREEN_HEIGHT / GAME_SCALE)  # 240 world pixels

# Art sizes, in world pixels
TILE_SIZE = 16
PLAYER_SPRITE_SIZE = 64  # one frame of the player sheets, before cropping to a tile

# Settings and audio
SETTINGS_FILE_PATH = "settings.json"  # in the project root (git-ignored)
DEFAULT_SETTINGS = {
    "fps_enabled": False,
    "full_screen_enabled": False,
    "screen_shake_enabled": True,
    "hurt_vignette_enabled": True,
    "music_volume": 0.5,
    "sfx_volume": 0.5,
}
SFX_FOLDER = "Assets/Sounds"
MUSIC_FOLDER = "Assets/Music"

# Shared UI
FONT_PATH = "Assets/Fonts/Silkscreen-Regular.ttf"
BUTTON_FONT_SIZE = 32  # every menu's buttons
PANEL_FRAME_PATH = "Assets/UI/panel_frame.png"  # 9-slice frame for HUD and inventory
# Corner size in art pixels; must match the panel_frame border in tools/make_sprite.py
PANEL_CORNER_SIZE = 4
OVERLAY_ALPHA = 160  # 0-255; how dark menus drawn over the game make it

# The run: floor maps in play order
FLOOR_ORDER = [
    "Assets/Maps/easy_floor_1.tmx",
]
