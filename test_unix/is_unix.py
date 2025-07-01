import magic
from pathlib import Path
import csv
import sys

def scan_for_excel_like_unix_files(scan_path: Path, output_file: str):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Full Path", "File Name", "Detected Type"])

        for file in scan_path.rglob("*"):
            if file.is_file() and not file.suffix:  # Only files with no extension
                try:
                    file_type = magic.from_file(str(file))
                    if "Excel" in file_type or "Composite Document File" in file_type:
                        writer.writerow([str(file.resolve()), file.name, file_type])
                except Exception as e:
                    print(f"Skipped {file}: {e}")

    print(f"\n✅ Scan complete. Results saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python is_unix.py /path/to/scan")
        sys.exit(1)

    scan_dir = Path(sys.argv[1])
    if not scan_dir.exists():
        print(f"❌ Error: {scan_dir} does not exist.")
        sys.exit(1)

    output_csv = "unix_files.csv"
    scan_for_excel_like_unix_files(scan_dir, output_csv)

