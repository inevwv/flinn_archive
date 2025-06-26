import os
import shutil
import csv
from pathlib import Path
from collections import defaultdict

# === Ask for source and extensions ===
source_input = input("Enter full path to the source folder: ").strip('"')
SOURCE_DIR = Path(source_input).resolve()

extensions_input = input("Enter file extensions to isolate (comma-separated, no dots): ")
extensions = [f".{ext.strip().lower()}" for ext in extensions_input.split(",")]

# === Define fixed staging and logging paths ===
EXCLUDE_DIR = SOURCE_DIR / "workspace"
STAGING_ROOT = SOURCE_DIR / "workspace" / "staging"
LOG_PATH = STAGING_ROOT / "copy_log.csv"

# === Prepare folders and logs ===
STAGING_ROOT.mkdir(parents=True, exist_ok=True)
log_entries = []
name_counter = defaultdict(int)

def is_within_exclude(path):
    try:
        path.relative_to(EXCLUDE_DIR)
        return True
    except ValueError:
        return False

def safe_filename(base_name, dest_dir):
    if not (dest_dir / base_name).exists():
        return base_name
    stem, ext = os.path.splitext(base_name)
    while True:
        name_counter[base_name] += 1
        candidate = f"{stem}_{name_counter[base_name]}{ext}"
        if not (dest_dir / candidate).exists():
            return candidate

# === Walk and copy ===
for root, dirs, files in os.walk(SOURCE_DIR):
    current_dir = Path(root)

    # Skip the workspace directory itself (prevents recursive self-copying)
    if is_within_exclude(current_dir):
        continue

    for file in files:
        ext = Path(file).suffix.lower()
        if ext in extensions:
            src_path = current_dir / file
            relative_path = src_path.relative_to(SOURCE_DIR)

            # Create destination dir by extension
            ext_dir = STAGING_ROOT / ext.strip(".")
            ext_dir.mkdir(parents=True, exist_ok=True)

            # Encode provenance into filename
            path_parts = list(relative_path.parts)
            dest_name = "_".join(path_parts)
            dest_name = safe_filename(dest_name, ext_dir)

            dest_path = ext_dir / dest_name
            shutil.copy2(src_path, dest_path)

            log_entries.append((str(src_path), str(dest_path)))

# === Write log ===
with open(LOG_PATH, mode='w', newline='', encoding='utf-8') as log_file:
    writer = csv.writer(log_file)
    writer.writerow(["original_path", "new_path"])
    writer.writerows(log_entries)

print(f"\n✅ Done! {len(log_entries)} files copied.\nLog saved to: {LOG_PATH}")
