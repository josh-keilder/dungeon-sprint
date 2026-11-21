# Dungeon Sprint

Dungeon Sprint is a 2D top-down dungeon adventure built with Python and Pygame. It features a modular architecture built from plain data and function-based systems, a menu/state system, and a single hand-built dungeon level with combat-adjacent player mechanics, items, enemies, doors, and a camera that follows the player through the map.

## Overview

The game currently includes:

- A main menu, options menu, and dungeon gameplay state
- Player movement with rolling, interaction, healing, and inventory controls
- Enemies, chests, doors, and collectible items
- A camera system that tracks the player across the dungeon
- GPU lighting: flickering torches and candles, a light around the player, and walls and closed doors that block light
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
- Sprite animation support for player, enemies, items and decor
- Lighting drawn by a ModernGL shader, with wall-blocked light and flame flicker
- Asset-driven map and object loading from TMX files

## Tech Stack

- Python
- pygame-ce (Pygame Community Edition)
- pytmx
- ModernGL (OpenGL rendering)

## Project Structure

The code is split into a reusable engine and the game built on it. `engine/` never imports the game; the pre-commit hook checks that on every commit.

- `main.py` - Dungeon Sprint's setup: settings, theme, window, renderer, sound and screens, then the engine's game loop
- `engine/` - Everything not specific to this game, for reuse in future pygame games:
  - `core/` - Game loop, screen switching, timers, settings, image loading, debug flags
  - `graphics/` - The OpenGL renderer and lighting, camera, display and letterboxing, animation, particles, screen shake, overlays, masks
  - `physics/` - Movement, knockback, wall collision, line of sight
  - `io/` - Input helpers and sound
  - `ui/` - Widgets (buttons, sliders, text labels, panels, health bars, titles, cursor, FPS counter) and the theme the game sets at startup
  - `gameplay/` - Health, stats, inventory, items and loot rolls
- `game/` - What Dungeon Sprint is:
  - `data/` - Every table: constants, the palette, enemy types, items, loot, particle presets, light types, sprite sheet layouts
  - `rules/` - Combat, the roll, the enemy sword swing, enemy behaviour, interaction, consumables, input bindings
  - `entities/` - The player and enemies
  - `world/` - Floors: map loading, tiles, and the objects placed on them (ground items, chests, crates)
  - `ui/` - HUD, inventory screen, floor transition, hit feedback and the hurt vignette
  - `states/` - The run, its death sequence, and the main, options and end-of-run menus
- `tools/` - Developer scripts: sprite generator, strip maker, map preview, ASCII → TMX map converter, the engine import check and the line counter (see [Developer Tools](#developer-tools))
- `hooks/` - Git pre-commit hook: formats staged files with isort and black, runs the engine import check, updates the statistics below
- `docs/` - How the code works
- `Assets/` - Sprites, maps, audio, fonts, and UI art

For how the code works, see the documentation in [docs/](docs/README.md): design rules, tooling, architecture, engine and game references, one frame step by step, data formats, how-to guides and reusing the engine.

## Running Locally

1. Create the project's virtual environment, `.venv`:

	```bash
	python -m venv .venv
	```

2. Install dependencies with:

	```bash
	.venv/Scripts/python -m pip install -r requirements.txt
	```

3. Launch the game:

	```bash
	.venv/Scripts/python main.py
	```

## Developer Tools

Run every tool from the project root as a module (`-m tools.<name>`), so it can import the game's code such as `game.data.constants`.

- **Sprite generator** (`tools/make_sprite.py`): regenerates every sprite drawn as text in its `SPRITES` dict (the UI panel frame, the speed boots) and saves them as PNGs in `Assets/`.

	```bash
	.venv/Scripts/python -m tools.make_sprite
	```

- **Map preview** (`tools/preview_map.py`): renders maps to PNGs in `map_previews/` (git-ignored), with the player spawn, enemy spawns, exit and door groups marked. With no arguments it previews every map in `FLOOR_ORDER`; pass map paths to preview only those.

	```bash
	.venv/Scripts/python -m tools.preview_map
	.venv/Scripts/python -m tools.preview_map Assets/Maps/Dungeon_Level_One.tmx
	```

- **ASCII → TMX converter** (`tools/ascii_to_tmx.py`): turns a floor sketched as text in `Assets/Maps/Source/` into a Tiled map in `Assets/Maps/`, with autotiled walls and automatic decor (torches, banners, wall rings, side torches, webs, rubble, bones, and candlesticks in treasure rooms). A second argument sets a different output path. The legend is in [docs/tooling.md](docs/tooling.md).

	```bash
	.venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/test_room.txt
	.venv/Scripts/python -m tools.ascii_to_tmx Assets/Maps/Source/test_room.txt Assets/Maps/other_name.tmx
	```

- **Strip maker** (`tools/make_strip.py`): joins animation frames from the original asset pack into one-row strips in `Assets/` (keys, the crate, torches and candlesticks). Needs the pack folder locally; it's git-ignored.

	```bash
	.venv/Scripts/python -m tools.make_strip
	```

- **Engine import check** (`tools/check_engine_imports.py`): fails if anything under `engine/` imports the game (`game`, `main` or `tools`). The pre-commit hook runs it on every commit.

	```bash
	.venv/Scripts/python tools/check_engine_imports.py
	```

- **Line counter** (`tools/line_counter.py`): updates the Project Statistics section of this README. The pre-commit hook runs it automatically; enable the hook once per clone with `git config core.hooksPath hooks`.

	```bash
	.venv/Scripts/python tools/line_counter.py
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
- **Total Files:** 86
- **Total Lines of Code:** 6566
