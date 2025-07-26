import csv
import sys
from pathlib import Path
from datetime import datetime

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    print("⚠️ python-magic not installed. MIME types will be empty.")

# Map legacy file extensions to modern equivalents
CONVERSION_MAP = {
    '.xls': 'xlsx',
    '.doc': 'docx',
    '.ppt': 'pptx',
    '.m4v': 'mp4',
    '.mov': 'mp4',
    '.mpg': 'mp4'
}

# Summary counters
total_files = 0
empty_files = 0
multiple_dots = 0
needs_conversion = 0
conversion_targets = {}
unknown_mime = 0


def get_file_inventory(root_dir, output_csv_path):
    global total_files, empty_files, multiple_dots, needs_conversion, conversion_targets, unknown_mime

    workspace_dir = Path(output_csv_path).resolve().parent

    ignore_folders = {
        '.fseventsd', '.Spotlight-V100', '.TemporaryItems', '.Trashes',
        '.DS_Store', '$RECYCLE.BIN', 'System Volume Information', 'Recovery', 'Config.Msi'
    }

    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Full_Path',
            'File_Name',
            'Extension',
            'Has_Multiple_Dots',
            'Needs_Conversion',
            'Convert_To',
            'Mime_Type',
            'Is_Empty',
            'Size_(bytes)',
            'Creation_Time',
            'Modification_Time',
            'Source',
            'Review_Notes'
        ])

        for path in Path(root_dir).rglob('*'):
            if path.is_file():
                try:
                    resolved_path = path.resolve()
                    relative_parts = resolved_path.relative_to(Path(root_dir).resolve()).parts

                    if workspace_dir in resolved_path.parents:
                        continue

                    if any(
                        part.startswith('.') or
                        part.startswith('$') or
                        part in ignore_folders
                        for part in relative_parts
                    ):
                        continue

                    # File stats
                    try:
                        stat = path.stat()
                        size = stat.st_size
                        creation_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
                        modification_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                        is_empty = 'Yes' if size == 0 else 'No'
                    except (PermissionError, OSError, FileNotFoundError):
                        size = ''
                        creation_time = 'ACCESS DENIED'
                        modification_time = 'ACCESS DENIED'
                        is_empty = 'Unknown'

                    dynamic_label = relative_parts[0] if relative_parts else ''

                    # Extension and dot logic
                    ext = path.suffix.lower()
                    dot_count = path.name.count('.')
                    has_multiple_dots = 'Yes' if dot_count >= 2 else 'No'

                    # Conversion logic
                    convert_to = CONVERSION_MAP.get(ext, '')
                    needs_conv = 'Yes' if convert_to else 'No'

                    # MIME type
                    if HAS_MAGIC:
                        try:
                            mime_type = magic.from_file(str(path), mime=True)
                        except Exception:
                            mime_type = ''
                    else:
                        mime_type = ''

                    # Update counters
                    total_files += 1
                    if is_empty == 'Yes':
                        empty_files += 1
                    if has_multiple_dots == 'Yes':
                        multiple_dots += 1
                    if needs_conv == 'Yes':
                        needs_conversion += 1
                        conversion_targets[convert_to] = conversion_targets.get(convert_to, 0) + 1
                    if HAS_MAGIC and not mime_type:
                        unknown_mime += 1

                    # Write row
                    writer.writerow([
                        str(resolved_path),
                        path.name,
                        ext,
                        has_multiple_dots,
                        needs_conv,
                        convert_to,
                        mime_type,
                        is_empty,
                        size,
                        creation_time,
                        modification_time,
                        dynamic_label,
                        ''  # Review notes (blank)
                    ])

                except (ValueError, RuntimeError):
                    continue


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python file_inventory.py [root_folder] [output_csv_path]")
    else:
        root_folder = sys.argv[1]
        output_csv_path = sys.argv[2]
        get_file_inventory(root_folder, output_csv_path)

        # Summary
        print("\n✅ Inventory complete!")
        print(f"📄 Output saved to: {output_csv_path}")
        print("\n📊 Inventory Summary:")
        print(f"   📁 Total files scanned: {total_files}")
        print(f"   🧹 Empty files: {empty_files}")
        print(f"   🌀 Files with multiple dots: {multiple_dots}")
        print(f"   🔁 Files needing conversion: {needs_conversion}")
        for fmt, count in conversion_targets.items():
            print(f"      ↳ Convert to .{fmt}: {count}")
        if HAS_MAGIC:
            print(f"   ❓ Files with unknown MIME type: {unknown_mime}")
        else:
            print("   ⚠️ MIME type detection was skipped (python-magic not installed).")
