import os

# Folders that aren't project code
IGNORED_FOLDERS = ("venv", ".git", "__pycache__", ".venv", ".claude")

# The README section this tool rewrites
STATS_HEADER = "\n## Project Statistics\n"


def count_lines_in_project(start_path=".", ignore_folders=IGNORED_FOLDERS):
    total_lines = 0
    file_count = 0

    for folder_path, folder_names, file_names in os.walk(start_path):
        folder_names[:] = [
            folder_name
            for folder_name in folder_names
            if folder_name not in ignore_folders
        ]

        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            try:
                if file_name.endswith(".py"):
                    with open(
                        file_path, "r", encoding="utf-8", errors="ignore"
                    ) as python_file:
                        line_count = sum(1 for line in python_file)
                        total_lines += line_count
                        file_count += 1
            except Exception:
                continue

    return total_lines, file_count


def update_readme(line_count, file_count, readme_path="README.md"):
    stats_header = STATS_HEADER
    stats_content = (
        f"- **Total Files:** {file_count}\n- **Total Lines of Code:** {line_count}\n"
    )

    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as readme_file:
            content = readme_file.read()

        if stats_header in content:
            main_content = content.split(stats_header)[0]
            new_content = main_content + stats_header + stats_content
        else:
            new_content = content + stats_header + stats_content
    else:
        new_content = stats_header + stats_content

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(new_content)
    print("README.md updated successfully!")


if __name__ == "__main__":
    total_lines, total_files = count_lines_in_project()
    update_readme(total_lines, total_files)
