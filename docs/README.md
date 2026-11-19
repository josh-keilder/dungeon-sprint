# Dungeon Sprint: how the code works

The code itself has no docstrings on purpose. Explanations live here so the source stays short and readable. Comments in the code are kept only where a line would be unclear on its own.

The project's `README.md` covers what the game is, how to install it and how to play it. These pages explain the code, in reading order:

| Page | What it covers |
| --- | --- |
| [Design rules](design-rules.md) | the engine and game split, the folders, state as plain dicts, the code style and file layout |
| [Tooling](tooling.md) | setup, formatting, the pre-commit hook, every tool in `tools/`, the debug keys |
| [Architecture](architecture.md) | startup, the game loop, the renderer and lighting, letterboxing, the screens and how they switch |
| [Reference](reference.md) | every module, folder by folder |
| [One frame](frame.md) | one gameplay frame, step by step |
| [Data formats](data-formats.md) | the shape of every table: enemy types, items, loot, maps, textures, settings |
| [How to](how-to.md) | adding enemies, items, floors and more |
| [Known gaps](known-gaps.md) | what's missing or planned |
