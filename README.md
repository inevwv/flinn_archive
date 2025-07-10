# 🗂️ Archive Recovery & File Inventory Project

This project is a cross-platform toolkit for auditing, organizing, and repairing decades of accumulated files from a professor’s digital archive. 
The primary goals are to:

* Identify and correct files with missing or incorrect extensions (e.g., Unix-originated files)
* Generate a clean inventory of all files
* Quarantine unknown or problematic files
* Prepare the dataset for long-term use, archival, or migration

---

## 🔧 Features

### 1. **File Type Detection & Repair (`fix_unix.py`)**

* Scans a directory for files without extensions
* Uses `python-magic` and optionally `ffprobe` to determine file types
* Renames files with appropriate extensions
* Supports dry-run mode and logs changes
* Quarantines unknown/skipped files to a safe folder (`/workspace/quarantine/`)
* Skips system folders and avoids recursive loops (e.g., skipping `/workspace/`)

### 2. **File Inventory (`get_file_inventory.py`)**

* Recursively crawls the source drive
* Records file metadata (path, name, extension, size, timestamps)
* Skips known system folders (e.g., `.DS_Store`, `$RECYCLE.BIN`, etc.)
* Outputs a clean `.csv` for tracking, auditing, or metadata tagging

### 3. **Extension-Based File Isolation (Optional)**

* Scripts can isolate file types (e.g., `.xls`, `.doc`, `.pct`) into staging folders for batch review or conversion

---

## 🖥️ Usage

### 1. Install dependencies

```bash
pip install python-magic
# If using ffprobe for video detection:
# brew install ffmpeg   # macOS
# choco install ffmpeg  # Windows (with Chocolatey)
```

### 2. Run file fixer with dry-run

```bash
python fix_unix.py --source D:\ --dry-run
```

### 3. Run file fixer and apply changes

```bash
python fix_unix.py --source D:\ --commit
```

### 4. Generate file inventory

```bash
python get_file_inventory.py --source D:\ --output inventory.csv
```

---

## 📁 Folder Structure

```
/D:/
├── workspace/
│   ├── staging/         ← Optional: holds isolated file types
│   ├── quarantine/      ← Skipped/unreadable files are stored here
├── fix_unix.py          ← File extension fixer script
├── get_file_inventory.py← CSV index generator
```

---

## 📝 Logs & Tracking

* Each operation (renamed, skipped, quarantined) is logged into a timestamped CSV
* Undo logs are generated to help roll back changes
* Supports traceability for long-term archival integrity

---

## 🧠 Notes

* File provenance is preserved through logging, not in-place renaming
* Use staging folders for manual QC or format conversion (e.g., `.xls` → `.xlsx`)
* Some files (e.g., from legacy macOS systems) may be unreadable or corrupt — these are automatically quarantined
