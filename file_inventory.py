import csv
import sys
from pathlib import Path
from datetime import datetime


def get_file_inventory(root_dir, output_csv_path):
    # Define workspace folder (resolved to absolute path)
    workspace_dir = Path('workspace').resolve()

    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Full Path',
            'File Name',
            'Extension',
            'Size (bytes)',
            'Creation Time',
            'Modification Time',
            'Source'
        ])

        for path in Path(root_dir).rglob('*'):
            if path.is_file():
                # Skip if file is inside the workspace folder
                try:
                    if workspace_dir in path.resolve().parents:
                        continue
                except RuntimeError:
                    # Catch symlink loops just in case
                    continue

                # Skip if any part of the path is hidden (starts with '.')
                try:
                    if any(part.startswith('.') for part in path.relative_to(root_dir).parts):
                        continue
                except ValueError:
                    # If relative_to fails (shouldn't happen), be safe
                    continue

                # File stats
                stat = path.stat()
                creation_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
                modification_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

                # Dynamic source label = first folder after root_dir
                try:
                    relative = path.relative_to(root_dir)
                    dynamic_label = relative.parts[0] if relative.parts else ''
                except ValueError:
                    dynamic_label = ''

                writer.writerow([
                    str(path.resolve()),
                    path.name,
                    path.suffix,
                    stat.st_size,
                    creation_time,
                    modification_time,
                    dynamic_label
                ])


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python file_inventory.py [root_folder] [output_csv_path]")
    else:
        root_folder = sys.argv[1]
        output_csv_path = sys.argv[2]
        get_file_inventory(root_folder, output_csv_path)
        print(f"Inventory saved to {output_csv_path}")

# python file_inventory.py "[root_dir]" "[output_csv]"
