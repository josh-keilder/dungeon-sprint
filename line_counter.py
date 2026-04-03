"""
Utility: Project Statistics Generator
------------------------------------
Scans the project directory to calculate the total number of Python files
and lines of code. The results are then automatically appended or updated
within the project's README.md file.

Functions:
    count_lines_in_project: Recursively counts files and lines, skipping specified folders.
    update_readme: Injects or updates a 'Project Statistics' section in README.md.
"""

import os


def count_lines_in_project(
    start_path=".", ignore_folders={"venv", ".git", "__pycache__"}
):
    """
    Walks through the directory tree and counts lines in all .py files.

    Args:
        start_path (str): The root directory to start the scan.
        ignore_folders (set): Directory names to exclude from the scan.

    Returns:
        tuple: (total_lines, file_count)
    """
    total_lines = 0
    file_count = 0

    for root, dirs, files in os.walk(start_path):
        # Modifying dirs in-place prevents os.walk from entering ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_folders]

        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.endswith(".py"):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = sum(1 for line in f)
                        total_lines += lines
                        file_count += 1
            except Exception:
                # Silently skip files that cannot be read (e.g., permission issues)
                continue

    return total_lines, file_count


def update_readme(lines, files, readme_path="README.md"):
    """
    Updates the README.md file with the provided statistics.
    If the statistics section exists, it is overwritten.
    """
    stats_header = "\n## Project Statistics\n"
    stats_content = f"- **Total Files:** {files}\n- **Total Lines of Code:** {lines}\n"

    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        if stats_header in content:
            # Locate the existing header and update the content below it
            main_content = content.split(stats_header)[0]
            new_content = main_content + stats_header + stats_content
        else:
            new_content = content + stats_header + stats_content
    else:
        new_content = stats_header + stats_content

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"README.md updated successfully!")


if __name__ == "__main__":
    total_l, total_f = count_lines_in_project()
    update_readme(total_l, total_f)
