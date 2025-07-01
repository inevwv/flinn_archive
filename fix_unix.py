import magic
from pathlib import Path
import csv
import sys

# Mapping from detected type keyword to extension
EXTENSION_MAP = {
    "Excel": "xls",
    "Word": "doc",
    "PowerPoint": "ppt",
    "Access": "mdb",
    "Outlook": "msg",
    "Composite Document File": "xls",  # based on your testing
}

DEFAULT_EXT = "xls"  # fallback if unknown

def get_extension(file_type: str) -> str:
    for keyword, ext in EXTENSION_MAP.items():
        if keyword in file_type:
            return ext
    return DEFAULT_EXT

def rename_unix_files(scan_dir: Path, log_file: str):
    with open(log_file, 'w', newline='', encoding='utf-8') as log:
        writer = csv.writer(log)
        writer.writerow(["Original Path", "New Path", "Detected Type", "Assigned Extension", "Status"])

        for file in scan_dir.rglob("*"):
            if file.is_file() and not file.suffix:
                try:
                    file_type = magic.from_file(str(file))
                    assigned_ext = get_extension(file_type)
                    new_path = file.with_name(file.name + f".{assigned_ext}")

                    if new_path.exists():
                        writer.writerow([file, new_path, file_type, assigned_ext, "Skipped (target exists)"])
                        continue

                    file.rename(new_path)
                    writer.writerow([file, new_path, file_type, assigned_ext, "Renamed"])
                except Exception as e:
                    writer.writerow([file, "", "", "", f"Error: {e}"])

    print(f"\n✅ Done. Log saved to: {log_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_unix.py /path/to/scan")
        sys.exit(1)

    scan_path = Path(sys.argv[1])
    if not scan_path.exists():
        print(f"❌ Error: {scan_path} does not exist.")
        sys.exit(1)

    log_filename = "renamed_unix_files_log.csv"
    rename_unix_files(scan_path, log_filename)
