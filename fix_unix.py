import magic
from pathlib import Path
import csv
import sys
import argparse

# Detected types → extensions
EXTENSION_MAP = {
    "Excel": "xls",
    "Word": "doc",
    "PowerPoint": "ppt",
    "Access": "mdb",
    "Outlook": "msg",
    "Composite Document File": "xls",  # based on your validation
}

DEFAULT_EXT = "xls"  # fallback

def get_extension(file_type: str) -> str:
    for keyword, ext in EXTENSION_MAP.items():
        if keyword in file_type:
            return ext
    return DEFAULT_EXT

def fix_unix_files(scan_dir: Path, dry_run: bool):
    rename_log = "renamed_unix_files_log.csv"
    undo_log = "undo_log.csv"

    with open(rename_log, 'w', newline='', encoding='utf-8') as rename_logfile, \
         open(undo_log, 'w', newline='', encoding='utf-8') as undo_logfile:

        rename_writer = csv.writer(rename_logfile)
        undo_writer = csv.writer(undo_logfile)

        rename_writer.writerow(["Original Path", "New Path", "Detected Type", "Assigned Extension", "Status"])
        undo_writer.writerow(["New Path", "Original Path"])

        for file in scan_dir.rglob("*"):
            try:
                # Skip anything in excluded dirs
                if any(part in {
                    '.fseventsd', '.Spotlight-V100', '.TemporaryItems', '.Trashes', '.DS_Store',
                    '$RECYCLE.BIN', 'System Volume Information', 'Recovery', 'Config.Msi',
                    '__MACOSX', 'node_modules', '.cache', '.git'
                } for part in file.parts):
                    continue

                if file.is_file() and not file.suffix:
                    file_type = magic.from_file(str(file))
                    assigned_ext = get_extension(file_type)
                    new_path = file.with_name(file.name + f".{assigned_ext}")

                    if new_path.exists():
                        rename_writer.writerow([file, new_path, file_type, assigned_ext, "Skipped (target exists)"])
                        continue

                    if dry_run:
                        print(f"[DRY RUN] Would rename: {file} → {new_path}")
                        rename_writer.writerow([file, new_path, file_type, assigned_ext, "Dry run – not renamed"])
                    else:
                        file.rename(new_path)
                        rename_writer.writerow([file, new_path, file_type, assigned_ext, "Renamed"])
                        undo_writer.writerow([new_path, file])

            except Exception as e:
                rename_writer.writerow([file, "", "", "", f"Error: {e}"])

    print(f"\n✅ Done. Logs saved to: {rename_log}, {undo_log}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix misclassified Unix executable files by renaming them with proper extensions.")
    parser.add_argument("path", help="Root folder or drive to scan")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without renaming files")

    args = parser.parse_args()
    scan_path = Path(args.path)

    if not scan_path.exists():
        print(f"❌ Error: {scan_path} does not exist.")
        sys.exit(1)

    fix_unix_files(scan_path, dry_run=args.dry_run)
