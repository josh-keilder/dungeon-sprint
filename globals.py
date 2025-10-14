import pygame

SCREENWIDTH = 1280
SCREENHEIGHT = 720
FRAMERATE = 60
TILESIZE = 16
PLAYER_SPRITESIZE = 64

# Colors
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
RED         = (255, 0, 0)
GREEN       = (0, 255, 0)
BLUE        = (0, 0, 255)
YELLOW      = (255, 255, 0)
CYAN        = (0, 255, 255)
MAGENTA     = (255, 0, 255)
ORANGE      = (255, 165, 0)
PURPLE      = (128, 0, 128)
PINK        = (255, 192, 203)
BROWN       = (139, 69, 19)
GRAY        = (128, 128, 128)
LIGHT_GRAY  = (192, 192, 192)
DARK_GRAY   = (64, 64, 64)


# --- Images ---
""" All images are stored in the globals file to allow for easier locating when changes are needed."""

# Start Screen images
START_SCREEN_IMAGE = pygame.image.load('Assets/Menu-Assets/start-screen_1.png')
START_BUTTON_IMAGE = pygame.image.load('Assets/Menu-Assets/start-button.png')
EXIT_BUTTON_IMAGE = pygame.image.load('Assets/Menu-Assets/exit-button.png')
OPTIONS_BUTTON_IMAGE = pygame.image.load('Assets/Menu-Assets/options-button.png')

# Options Screen images
OPTIONS_SCREEN_IMAGE = pygame.image.load('Assets/Menu-Assets/options-screen.png')
MAIN_MENU_BUTTON_IMAGE = pygame.image.load('Assets/Menu-Assets/main-menu-button.png')
BACK_BUTTON_IMAGE = pygame.image.load('Assets/Menu-Assets/back-button.png')

FPS_BUTTON_ON_IMAGE = pygame.image.load('Assets/Menu-Assets/Fps_On.png')
FPS_BUTTON_OFF_IMAGE = pygame.image.load('Assets/Menu-Assets/Fps_Off.png')


# Dungeon Level Maps
DUNGEON_LEVEL_ONE = "Assets/Maps/Dungeon_Level_One.tmx"