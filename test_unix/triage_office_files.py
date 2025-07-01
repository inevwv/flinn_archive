import csv
import shutil
from pathlib import Path

# Input and output paths
input_csv = "unix_files.csv"
base_output_dir = Path("D:/workspace/staging/")
log_csv = "triage_log.csv"

# Map detected strings to extension
EXTENSION_MAP = {
    "Excel": "xls",
    "Word": "doc",
    "PowerPoint": "ppt",
    "Access": "mdb",
    "Outlook": "msg",
    "Composite Document File": "unknown",  # could be anything Office
}

# Fallback if nothing matches
DEFAULT_EXT = "unknown"

# Create output directory
base_output_dir.mkdir(parents=True, exist_ok=True)

# Start processing
with open(input_csv, newline='', encoding='utf-8') as infile, \
     open(log_csv, 'w', newline='', encoding='utf-8') as logfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(logfile)
    writer.writerow([
        "Original Path",
        "New Path",
        "Detected Type",
        "Assigned Extension",
        "Status"
    ])

    for row in reader:
        original_path = Path(row["Full Path"])
        file_type = row["Detected Type"]

        if not original_path.exists():
            writer.writerow([original_path, "", file_type, "", "File not found"])
            continue

        # Determine best match extension
        assigned_ext = DEFAULT_EXT
        for keyword, ext in EXTENSION_MAP.items():
            if keyword in file_type:
                assigned_ext = ext
                break

        output_subdir = base_output_dir / assigned_ext
        output_subdir.mkdir(parents=True, exist_ok=True)

        new_name = original_path.name + f".{assigned_ext}"
        dest_path = output_subdir / new_name

        try:
            if dest_path.exists():
                writer.writerow([original_path, dest_path, file_type, assigned_ext, "Skipped (already exists)"])
                continue

            shutil.copy2(original_path, dest_path)
            writer.writerow([original_path, dest_path, file_type, assigned_ext, "Copied and renamed"])
        except Exception as e:
            writer.writerow([original_path, "", file_type, assigned_ext, f"Error: {e}"])

print(f"\n✅ Done. Files sorted into {base_output_dir}, log saved to {log_csv}")
