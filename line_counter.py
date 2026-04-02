import os

def count_lines_in_project(start_path='.', ignore_folders={'venv', '.git', '__pycache__'}):
    total_lines = 0
    file_count = 0

    for root, dirs, files in os.walk(start_path):
        # Efficiently skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_folders]

        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.endswith('.py'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = sum(1 for line in f)
                        total_lines += lines
                        file_count += 1
            except Exception:
                continue 

    return total_lines, file_count

def update_readme(lines, files, readme_path='README.md'):
    stats_header = "\n## 📊 Project Statistics\n"
    stats_content = f"- **Total Files:** {files}\n- **Total Lines of Code:** {lines}\n"

    # Read existing content to check if stats already exist
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # If the header exists, we replace the old stats; otherwise, we append.
        if stats_header in content:
            # Simple approach: find the header and overwrite everything after it
            main_content = content.split(stats_header)[0]
            new_content = main_content + stats_header + stats_content
        else:
            new_content = content + stats_header + stats_content
    else:
        new_content = stats_header + stats_content

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"README.md updated successfully!")

if __name__ == "__main__":
    total_l, total_f = count_lines_in_project()
    update_readme(total_l, total_f)