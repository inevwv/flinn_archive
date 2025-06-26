import csv
import sys
from pathlib import Path
from datetime import datetime

def get_file_inventory(root_dir, output_csv_path):
    workspace_dir = Path('workspace').resolve()

    # Set of known system folder names to skip (macOS + Windows)
    ignore_folders = {
        '.fseventsd',
        '.Spotlight-V100',
        '.TemporaryItems',
        '.Trashes',
        '.DS_Store',
        '$RECYCLE.BIN',
        'System Volume Information',
        'Recovery',
        'Config.Msi'
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
                try:
                    resolved_path = path.resolve()
                    relative_parts = resolved_path.relative_to(Path(root_dir).resolve()).parts

                    # Skip if inside workspace
                    if workspace_dir in resolved_path.parents:
                        continue

                    # Skip hidden or system folders
                    if any(
                            part.startswith('.') or
                            part.startswith('$') or
                            part in ignore_folders
                            for part in relative_parts
                    ):
                        continue

                    # Try getting file stats and fallback gracefully
                    try:
                        stat = path.stat()
                        size = stat.st_size
                        creation_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
                        modification_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    except (PermissionError, OSError, FileNotFoundError):
                        size = ''
                        creation_time = 'ACCESS DENIED'
                        modification_time = 'ACCESS DENIED'

                    dynamic_label = relative_parts[0] if relative_parts else ''

                    writer.writerow([
                        str(resolved_path),
                        path.name,
                        path.suffix,
                        size,
                        creation_time,
                        modification_time,
                        dynamic_label
                    ])

                except (ValueError, RuntimeError):
                    continue


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python file_inventory.py [root_folder] [output_csv_path]")
    else:
        root_folder = sys.argv[1]
        output_csv_path = sys.argv[2]
        get_file_inventory(root_folder, output_csv_path)
        print(f"Inventory saved to {output_csv_path}")


# python file_inventory.py "[root_dir]" "[output_csv]"
