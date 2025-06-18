import csv
import sys
from pathlib import Path
from datetime import datetime

def get_file_inventory(root_dir, output_csv, source_label):
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
                writer.writerow([
                    str(path.resolve()),
                    path.name,
                    path.suffix,
                    stat.st_size,
                    creation_time,
                    modification_time,
                    source_label
                ])

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python file_inventory.py [root_folder] [output_csv] [source_label]")
    else:
        root_folder = sys.argv[1]
        output_csv = sys.argv[2]
        source_label = sys.argv[3]
        get_file_inventory(root_folder, output_csv, source_label)
        print(f"Inventory saved to {output_csv}")

# python file_inventory.py "[root_folder]" "[output_csv]" "[source_label]"
