import math

# Screen, timing, and sprite sizes
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FRAME_RATE = 240
TILE_SIZE = 16
PLAYER_SPRITE_SIZE = 64

# World canvas, drawn at 1x then scaled up by GAME_SCALE
GAME_SCALE = 3
WORLD_WIDTH = math.ceil(SCREEN_WIDTH / GAME_SCALE)
WORLD_HEIGHT = math.ceil(SCREEN_HEIGHT / GAME_SCALE)

# Gameplay distances
UNLOCK_DOOR_DISTANCE = 32

# Item Values
SMALL_HEALTH_POTION_VALUE = 70

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)

# Tileset palette, for UI that should match the art
PALETTE_VOID = (37, 19, 26)
PALETTE_SHADOW = (84, 55, 64)
PALETTE_BLOOD = (188, 76, 81)
PALETTE_STEEL = (173, 193, 207)

# Kept in case I need this specific color
OPTION_MENU_BUTTON_BACKGROUND = (110, 74, 72)

MENU_BACKGROUND_COLOR = PALETTE_VOID


DUNGEON_LEVEL_ONE = "Assets/Maps/Dungeon_Level_One.tmx"

FONT_PATH = "Assets/Fonts/Silkscreen-Regular.ttf"
BUTTON_FONT_SIZE = 32

OVERLAY_ALPHA = 160
