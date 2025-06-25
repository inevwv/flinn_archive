import csv
import sys
from pathlib import Path
from datetime import datetime

def get_file_inventory(root_dir, output_csv_path):
    # Absolute path to workspace folder (used for skipping)
    workspace_dir = Path('workspace').resolve()

    # Set of system folders to skip explicitly (macOS junk folders, etc.)
    ignore_folders = {
        '.fseventsd',
        '.Spotlight-V100',
        '.TemporaryItems',
        '.Trashes',
        '.DS_Store'
    }

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
                # ✅ Skip if inside the workspace folder
                try:
                    if workspace_dir in path.resolve().parents:
                        continue
                except RuntimeError:
                    continue

                # ✅ Get relative parts safely
                try:
                    relative_parts = path.resolve().relative_to(Path(root_dir).resolve()).parts
                except ValueError:
                    continue

                # ✅ Skip if any folder in the path is hidden or matches ignored system folders
                if any(part.startswith('.') or part in ignore_folders for part in relative_parts):
                    continue

                # File stats
                stat = path.stat()
                creation_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
                modification_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

                # Dynamic source label = top-level folder name under root_dir
                dynamic_label = relative_parts[0] if relative_parts else ''

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
