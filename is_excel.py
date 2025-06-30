# istg this fuck as man cant name for shittt

1. find unix files or files without extensions


import magic
from pathlib import Path
import csv

scan_dir = Path("/path/to/folder")
output_file = "possible_excel_files.csv"

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["File", "Detected Type"])

    for file in scan_dir.iterdir():
        if file.is_file():
            file_type = magic.from_file(str(file))
            if "Excel" in file_type or "Composite Document File" in file_type:
                writer.writerow([file.name, file_type])

print(f"Done. Results saved to {output_file}")
