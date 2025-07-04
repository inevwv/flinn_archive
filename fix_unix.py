import magic
import subprocess
from pathlib import Path
import csv
import sys
import argparse

# Office/document file type keywords → extensions
EXTENSION_MAP = {
    # 🧩 Office / Document formats
    "Excel": "xls",
    "Word": "doc",
    "PowerPoint": "ppt",
    "Access": "mdb",
    "Outlook": "msg",
    "Composite Document File": "xls",  # Legacy Office files

    # 🖼️ Image formats
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
    "Camera Raw": "cr2",  # Canon RAW
    "Canon CR3": "cr3",   # Canon newer RAW
    "Nikon": "nef",
    "Sony": "arw",
    "Fujifilm": "raf",
    "Olympus": "orf",
}


# ffprobe format → extensions
VIDEO_EXT_MAP = {
    'mov,mp4,m4a,3gp,3g2,mj2': 'mp4',
    'avi': 'avi',
    'mpeg': 'mpg',
    'vob': 'vob',
    'matroska,webm': 'mkv',
    'mod': 'mod',
    'mts,m2ts': 'mts',
}

DEFAULT_EXT = "xls"

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
    'thumbs.db', '.ds_store'
}


def get_extension_magic(file_type: str) -> str | None:
    file_type = file_type.lower()
    for keyword, ext in EXTENSION_MAP.items():
        if keyword.lower() in file_type:
            return ext
    return None  # No match found

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
    except Exception:
        pass
    return None


def fix_unix_files(scan_dir: Path, dry_run: bool):
    rename_log = "renamed_unix_files_log.csv"
    undo_log = "undo_log.csv"

    with open(rename_log, 'w', newline='', encoding='utf-8') as rename_logfile, \
         open(undo_log, 'w', newline='', encoding='utf-8') as undo_logfile:

        rename_writer = csv.writer(rename_logfile)
        undo_writer = csv.writer(undo_logfile)

        rename_writer.writerow(["Original Path", "New Path", "Detection Method", "Assigned Extension", "Status"])
        undo_writer.writerow(["New Path", "Original Path"])

        for file in scan_dir.rglob("*"):
            try:
                # Skip excluded directories
                if any(part in EXCLUDED_DIRS for part in file.parts):
                    continue

                if (
                        file.name.startswith("._") or  # AppleDouble
                        file.name.startswith('.') or  # Hidden files like .ipspot_update or .localized
                        file.name.lower() in SKIP_FILENAMES or
                        file.stat().st_size == 0 or
                        any(skip in part.lower() for skip in SKIP_PATH_PARTS for part in file.parts)
                ):
                    continue

                if file.is_file() and not file.suffix:
                    # Try ffprobe
                    ffprobe_result = guess_extension_ffprobe(file)
                    if ffprobe_result:
                        assigned_ext, detection_method = ffprobe_result
                    else:
                        file_type = magic.from_file(str(file))
                        assigned_ext = get_extension_magic(file_type)
                        detection_method = f"magic: {file_type}"

                        if not assigned_ext:
                            rename_writer.writerow([file, "", detection_method, "", "Skipped (no known extension)"])
                            continue

                    new_path = file.with_name(file.name + f".{assigned_ext}")

                    if new_path.exists():
                        rename_writer.writerow([file, new_path, detection_method, assigned_ext, "Skipped (target exists)"])
                        continue

                    if dry_run:
                        print(f"[DRY RUN] Would rename: {file} → {new_path} [{detection_method}]")
                        rename_writer.writerow([file, new_path, detection_method, assigned_ext, "Dry run – not renamed"])
                    else:
                        file.rename(new_path)
                        rename_writer.writerow([file, new_path, detection_method, assigned_ext, "Renamed"])
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
