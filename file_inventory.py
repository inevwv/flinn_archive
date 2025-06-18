import csv
import sys
from pathlib import Path
from datetime import datetime

def get_file_inventory(root_dir, output_csv):
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
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
                stat = path.stat()
                creation_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
                modification_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                # New: get subfolder label relative to root_dir
                try:
                    relative = path.relative_to(root_dir)
                    dynamic_label = relative.parts[0] if relative.parts else ''
                except ValueError:
                    # fallback if relative fails (shouldn’t happen)
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
        print("Usage: python file_inventory.py [root_folder] [output_csv]")
    else:
        root_folder = sys.argv[1]
        output_csv = sys.argv[2]
        get_file_inventory(root_folder, output_csv)
        print(f"Inventory saved to {output_csv}")

# python file_inventory.py "[root_dir]" "[output_csv]"
