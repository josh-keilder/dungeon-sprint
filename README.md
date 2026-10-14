# Dungeon Sprint

Dungeon Sprint is a 2D top-down dungeon adventure built with Python and Pygame. It features a modular architecture built from plain data and function-based systems, a menu/state system, and a single hand-built dungeon level with combat-adjacent player mechanics, items, enemies, doors, and a camera that follows the player through the map.

## Overview

The game currently includes:

- A start menu, options menu, and dungeon gameplay state
- Player movement with rolling, interaction, healing, and inventory controls
- Enemies, chests, doors, and collectible items
- A camera system that tracks the player across the dungeon
- Health bars for the player and enemies
- Audio handling for menu and gameplay events
- TMX map loading with layered tiles and object placement

## Controls

- `WASD` - Move
- `SPACE` - Roll while moving
- `F` - Interact with chests, doors, and nearby items
- `E` - Toggle inventory
- `Q` - Use a small health potion if available
- `ESC` - Open the options/pause menu
- `P` - Toggle hitbox debug rendering
- `Mouse click` - Manage inventory while it is open

## Features

- State-based flow for menus and gameplay
- Camera-follow dungeon traversal
- Collision-driven interactions with the world
- Inventory management with stackable items and equipment slots
- Health and healing systems
- Sprite animation support for player and enemies
- Asset-driven map and object loading from TMX files

## Tech Stack

- Python
- pygame-ce (Pygame Community Edition)
- pytmx

## Project Structure

- `main.py` - Game startup and main loop
- `globals.py` - Shared constants: screen size, tile size, colors, map path
- `entities/` - Player and enemy classes, their stats and sprite data
- `items/` - Item classes, item database, sprite data, and loot tables
- `states/` - Game state manager, dungeon level and map loading, start and options menus
- `systems/` - Gameplay rules as function modules: input, movement, roll, combat, health, inventory, camera, sound, settings, and more
- `ui_objects/` - Buttons, sliders, text labels, health bars, inventory screen, cursor
- `tools/` - Developer scripts (line counter used by the pre-commit hook)
- `hooks/` - Git pre-commit hook
- `Assets/` - Sprites, maps, audio, and UI art

For a full explanation of how the code works, see [Project_Documentation.md](Project_Documentation.md).

## Running Locally

1. Create and activate a Python virtual environment.
2. Install dependencies with:

	```bash
	pip install -r requirements.txt
	```

3. Launch the game:

	```bash
	python main.py
	```

## Development Notes

- The game is currently centered around a single dungeon level.
- Content is organized for expansion into more maps, enemies, items, and progression systems.
- Debug hitboxes can be enabled in-game with `P`.

## Planned Improvements

- Additional dungeon levels
- Enemy AI improvements
- Boss encounters
- Saving and loading
- Expanded UI and menus
- More items, equipment, and progression systems

## Project Statistics
- **Total Files:** 47
- **Total Lines of Code:** 2368
