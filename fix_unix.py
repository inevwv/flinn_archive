import magic
import subprocess
from pathlib import Path
import csv
import sys
import argparse
import os

# --- Extension mapping based on libmagic keywords ---
EXTENSION_MAP = {
    # Office/doc formats
    "Excel": "xls",
    "Word": "doc",
    "PowerPoint": "ppt",
    "Access": "mdb",
    "Outlook": "msg",
    "Composite Document File": "xls",
    "PDF document": "pdf",

    # Image formats
    "TIFF image": "tif",
    "Targa image": "tga",
    "JPEG image": "jpg",
    "JFIF": "jpg",
    "PNG image": "png",
    "GIF image": "gif",
    "PC bitmap": "bmp",
    "Bitmap": "bmp",
    "Photoshop": "psd",
    "PostScript": "eps",
    "Camera Raw": "cr2",
    "Canon CR3": "cr3",
    "Nikon": "nef",
    "Sony": "arw",
    "Fujifilm": "raf",
    "Olympus": "orf",
}

# --- Video format mapping based on ffprobe results ---
VIDEO_EXT_MAP = {
    'mov,mp4,m4a,3gp,3g2,mj2': 'mp4',
    'avi': 'avi',
    'mpeg': 'mpg',
    'vob': 'vob',
    'matroska,webm': 'mkv',
    'mod': 'mod',
    'mts,m2ts': 'mts',
}

# --- Directory and file filters to skip known junk or system folders ---
EXCLUDED_DIRS = {
    '.fseventsd', '.Spotlight-V100', '.TemporaryItems', '.Trashes', '.DS_Store',
    '$RECYCLE.BIN', 'System Volume Information', 'Recovery', 'Config.Msi',
    '__MACOSX', 'node_modules', '.cache', '.git'
}

SKIP_PATH_PARTS = {
    'imovie projects.localized',
    '.rcproject',
}

SKIP_FILENAMES = {
    'thumbs.db', '.ds_store', '.localized', '.ipspot_update'
}


# --- Append a flag to the name and resolve conflicts by adding counters if needed ---
def resolve_conflict_with_flag(target_path: Path, flag: str = "__DUPLICATE") -> Path:
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    new_stem = f"{stem}{flag}"
    new_path = parent / f"{new_stem}{suffix}"
    counter = 1
    while new_path.exists():
        new_path = parent / f"{new_stem}_{counter}{suffix}"
        counter += 1
    return new_path


# --- Try to assign an extension using magic's output string ---
def get_extension_magic(file_type: str) -> str | None:
    file_type = file_type.lower()
    for keyword, ext in EXTENSION_MAP.items():
        if keyword.lower() in file_type:
            return ext
    if file_type.strip() in {"data", "data file"}:
        return "xls"
    return None


# --- Try to assign a video extension using ffprobe ---
def guess_extension_ffprobe(file_path: Path) -> tuple[str, str] | None:
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=format_name',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(file_path)],
            capture_output=True, text=True, timeout=3
        )
        fmt_string = result.stdout.strip().lower()
        formats = [f.strip() for f in fmt_string.split(',')]
        for f in formats:
            for key, ext in VIDEO_EXT_MAP.items():
                key_formats = [k.strip() for k in key.split(',')]
                if f in key_formats:
                    return ext, f"ffprobe: {fmt_string}"
    except subprocess.SubprocessError:
        pass
    return None


# --- Main file fixing function ---
def fix_unix_files(scan_dir: Path, dry_run: bool):
    rename_log = "renamed_unix_files_log.csv"
    undo_log = "undo_log.csv"

    # --- Open logs for writing ---
    with open(rename_log, 'w', newline='', encoding='utf-8') as rename_logfile, \
            open(undo_log, 'w', newline='', encoding='utf-8') as undo_logfile:

        rename_writer = csv.writer(rename_logfile)
        undo_writer = csv.writer(undo_logfile)

        rename_writer.writerow(["Original Path", "New Path", "Detection Method", "Assigned Extension", "Status"])
        undo_writer.writerow(["New Path", "Original Path"])

        # --- Scan files recursively ---
        for file in scan_dir.rglob("*"):
            try:
                # Skip excluded directories, system files, or zero-byte files
                if any(part in EXCLUDED_DIRS for part in file.parts):
                    continue
                if "workspace" in file.relative_to(scan_dir).parts:
                    continue
                if (
                        file.name.startswith("._") or
                        file.name.startswith('.') or
                        file.name.lower() in SKIP_FILENAMES or
                        file.stat().st_size == 0 or
                        any(skip in part.lower() for skip in SKIP_PATH_PARTS for part in file.parts)
                ):
                    continue

                # --- Process extensionless files only ---
                if file.is_file() and not file.suffix:
                    # Skip files without write permission
                    if not os.access(file, os.W_OK):
                        print(f"⚠️ Skipped (no write permission): {file}")
                        rename_writer.writerow([file, "", "", "", "Skipped – no write permission"])
                    continue

                    # Try detecting video format using ffprobe first
                    ffprobe_result = guess_extension_ffprobe(file)
                    if ffprobe_result:
                        assigned_ext, detection_method = ffprobe_result
                    else:
                        # Fallback to libmagic detection
                        file_type = magic.from_file(str(file))
                        detection_method = f"magic: {file_type}"

                        # Special case for HFS resource fork
                        if "Apple HFS/HFS+ resource fork" in file_type:
                            new_path = file.with_name(file.name + ".TODELETE")
                            if dry_run:
                                print(f"[DRY RUN] Would rename resource fork: {file} → {new_path}")
                                rename_writer.writerow([file, new_path, detection_method, ".TODELETE",
                                                        "Dry run – would rename (resource fork)"])
                            else:
                                try:
                                    file.rename(new_path)
                                    print(f"🗑️ Marked for deletion: {file} → {new_path}")
                                    rename_writer.writerow([file, new_path, detection_method, ".TODELETE",
                                                            "Marked for Deletion (Resource Fork)", "No"])

                                    undo_writer.writerow([new_path, file])
                                except (OSError, IOError, PermissionError) as e:
                                    print(f"⚠️ Failed to rename resource fork: {file} → {new_path}: {e}")
                                    rename_writer.writerow(
                                        [file, "", detection_method, ".TODELETE", f"Error: failed to rename: {e}",
                                         "No"])
                            continue

                        assigned_ext = get_extension_magic(file_type)

                    # --- Quarantine unknown types ---
                    if not assigned_ext:
                        if dry_run:
                            print(f"[DRY RUN] Would quarantine: {file} → workspace/quarantine/")
                            rename_writer.writerow(
                                [file, "", detection_method, "", "Dry run – would quarantine (no known extension)"])
                        else:
                            quarantine_dir = Path("workspace/quarantine")
                            quarantine_dir.mkdir(parents=True, exist_ok=True)
                            quarantine_copy = quarantine_dir / file.name
                            if quarantine_copy.exists():
                                quarantine_copy = resolve_conflict_with_flag(quarantine_copy)
                            try:
                                quarantine_copy.write_bytes(file.read_bytes())
                                print(f"☣️ Quarantined: {file} → {quarantine_copy}")
                                rename_writer.writerow(
                                    [file, quarantine_copy, detection_method, "", "Quarantined (no known extension)"])
                            except Exception as e:
                                print(f"⚠️ Failed to copy {file} to quarantine: {e}")
                                rename_writer.writerow(
                                    [file, "", detection_method, "", f"Error: failed to quarantine: {e}"])
                        continue

                    # --- Assign new filename with extension ---
                    new_path = file.with_name(file.name + f".{assigned_ext}")

                    # Handle conflict by adding duplicate marker
                    if new_path.exists():
                        resolved_path = resolve_conflict_with_flag(new_path)
                        if dry_run:
                            print(
                                f"[DRY RUN] Would rename (conflict flagged): {file} → {resolved_path} [{detection_method}]")
                            rename_writer.writerow([file, resolved_path, detection_method, assigned_ext,
                                                    "Dry run – flagged potential duplicate"])
                        else:
                            file.rename(resolved_path)
                            rename_writer.writerow([file, resolved_path, detection_method, assigned_ext,
                                                    "Renamed (flagged potential duplicate)"])
                            undo_writer.writerow([resolved_path, file])
                        continue

                    # --- Standard renaming ---
                    if dry_run:
                        print(f"[DRY RUN] Would rename: {file} → {new_path} [{detection_method}]")
                        rename_writer.writerow(
                            [file, new_path, detection_method, assigned_ext, "Dry run – not renamed"])
                    else:
                        file.rename(new_path)
                        rename_writer.writerow([file, new_path, detection_method, assigned_ext, "Renamed"])
                        undo_writer.writerow([new_path, file])

            except Exception as e:
                rename_writer.writerow([file, "", "", "", f"Error: {e}"])

    print(f"
    ✅ Done.Logs
    saved
    to: {rename_log}, {undo_log}
    ")

    # --- Summary stats ---
    total = renamed = quarantined = skipped = 0
    with open(rename_log, newline='', encoding='utf-8') as f:
        next(f)  # skip header
    for row in csv.reader(f):
        total += 1
    match row[4].lower():
    case
    s
    if "rename" in s:
        renamed += 1
    case
    s
    if "quarantine" in s:
        quarantined += 1
    case
    s
    if "skip" in s:
        skipped += 1

    print(f"📊 Summary: Total processed: {total} | Renamed: {renamed} | Quarantined: {quarantined} | Skipped: {skipped}")

    # --- CLI Entry Point ---
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Fix Unix-like extensionless files with proper extensions.")
    parser.add_argument("path", help="Root folder or drive to scan")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without renaming or quarantining files")

    args = parser.parse_args()
    scan_path = Path(args.path)

    if not scan_path.exists():
        print(f"❌ Error: {scan_path} does not exist.")
    sys.exit(1)

    fix_unix_files(scan_path, dry_run=args.dry_run)
