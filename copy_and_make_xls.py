import csv
import shutil
from pathlib import Path

input_csv = "unix_files.csv"
output_dir = Path("D:/workspace/staging/xls")
log_csv = "copied_and_renamed_log.csv"

output_dir.mkdir(parents=True, exist_ok=True)

with open(input_csv, newline='', encoding='utf-8') as infile, \
     open(log_csv, 'w', newline='', encoding='utf-8') as logfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(logfile)
    writer.writerow(["Original Path", "Copied To", "Status"])

    for row in reader:
        original_path = Path(row["Full Path"])
        if not original_path.exists():
            writer.writerow([original_path, "", "File not found"])
            continue

        if original_path.suffix:
            writer.writerow([original_path, "", "Has extension already"])
            continue

        try:
            new_name = original_path.name + ".xls"
            dest_path = output_dir / new_name

            if dest_path.exists():
                writer.writerow([original_path, dest_path, "Skipped (already exists)"])
                continue

            shutil.copy2(original_path, dest_path)
            writer.writerow([original_path, dest_path, "Copied and renamed"])
        except Exception as e:
            writer.writerow([original_path, "", f"Error: {e}"])

print(f"\n✅ Done. Files copied to {output_dir}, log saved to {log_csv}")
