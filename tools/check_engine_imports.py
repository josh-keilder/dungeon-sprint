import ast
import os
import sys

# The engine must never import the game: everything under engine/ has to work in a new
# game with none of Dungeon Sprint's code. These are the game's top-level modules.
GAME_MODULES = ("game", "main", "tools")
ENGINE_FOLDER = "engine"

# Folders that aren't code
IGNORED_FOLDERS = ("__pycache__",)


def find_game_imports(engine_folder=ENGINE_FOLDER):
    problems = []

    for folder_path, folder_names, file_names in os.walk(engine_folder):
        folder_names[:] = [
            folder_name
            for folder_name in folder_names
            if folder_name not in IGNORED_FOLDERS
        ]

        for file_name in file_names:
            if file_name.endswith(".py"):
                problems.extend(game_imports_in(os.path.join(folder_path, file_name)))

    return problems


def game_imports_in(file_path):
    with open(file_path, "r", encoding="utf-8") as python_file:
        tree = ast.parse(python_file.read(), file_path)

    problems = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            modules = [node.module]
        else:
            continue

        for module in modules:
            if module.split(".")[0] in GAME_MODULES:
                problems.append(f"{file_path}:{node.lineno}: imports {module}")

    return problems


if __name__ == "__main__":
    problems = find_game_imports()
    for problem in problems:
        print(problem)

    if problems:
        print("The engine imports the game; pass the game's data in instead.")
        sys.exit(1)

    print("Engine imports: clean")
