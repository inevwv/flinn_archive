# 🗂️ Archive Restoration & Spreadsheet Comparison Toolkit

This cross-platform toolkit is designed to clean, convert, organize, and analyze decades of unstructured research files from a professor’s archive. It includes tools to fix malformed files, create an inventory, detect duplicates, and prepare data for analysis and long-term preservation.

---

## 📌 Project Goals

* Recover usable files from legacy sources (e.g. Unix-originated, malformed, or extensionless)
* Normalize file formats (e.g. `.xls` → `.xlsx`)
* Create a comprehensive, searchable file inventory
* Detect duplicate spreadsheets and surface mismatches
* Enable batch processing of archival materials across **Windows** and **macOS**

---

## 🧰 Core Tools & Scripts

### 🔧 `fix_unix.py`

Detects and fixes files without extensions using `python-magic` and optional `ffprobe`.

* Adds correct extensions based on MIME type
* Skips system/hidden folders
* Quarantines unknown types to `workspace/quarantine/`
* Supports `--dry-run` mode ~~for our anxious folks~~
* Logs actions to `rename_log.csv` and `undo_log.csv`

---

### 📋 `get_file_inventory.py`

Generates a CSV inventory of all files in a given directory.

* Records:

  * Full path
  * Name and extension
  * File size
  * Creation/modification dates
  * (Optional) MIME type
* Skips known system and temp folders
* Output helps guide QC and file migration

---

### 🔄 `convert_xls_from_csv_nocolumn.ps1`

PowerShell script to convert `.xls` files to `.xlsx` using Excel automation (Windows only).

* Ensures compatibility with modern spreadsheet tools
* Batch-runs silently, with failure detection and logging

---

### 🧪 `compare_spreadsheets.py`

Compares pairs of spreadsheets for content duplication.

* Detects:

  * Exact matches
  * Structural differences (columns, shape)
  * Missing/corrupt files
* Supports manual or CSV-based batch comparisons
* Logs results to `comparison_log.csv` or group-based logs

---

## 📁 Folder Structure

```
project_root/
├── fix_unix.py
├── get_file_inventory.py
├── compare_spreadsheets.py
├── batch_compare/
│   ├── automate_grouping.py
│   ├── convert_xls_from_csv_nocolumn.ps1
│   └── [comparison helpers]
├── workspace/
│   ├── quarantine/         ← Unknown or unfixable files
│   ├── converted_files/    ← .xls → .xlsx output
│   └── logs/               ← Rename/undo logs
├── data/
│   └── working_inventory.csv
├── results/
│   └── spreadsheet_comparison_log.csv
```

---

## 💻 Platform Support

| OS      | Status                      |
| ------- |-----------------------------|
| Windows | ✅ Fully supported           |
| macOS   | ⚠️ Partial (needs testing)* |

*file pathname may need adjusting

---

## 🔃 Typical Workflow

### 1. Fix malformed or extensionless files

```bash
python fix_unix.py --source /path/to/files --dry-run
python fix_unix.py --source /path/to/files --commit
```

### 2. Generate file inventory

```bash
python get_file_inventory.py --source /path/to/files --output workspace/inventory.csv
```

### 3. Convert `.xls` files to `.xlsx` (Windows)

```powershell
.\batch_compare\convert_xls_from_csv_nocolumn.ps1
```

### 4. Compare spreadsheets

**Manual:**

```bash
python compare_spreadsheets.py file1.xlsx file2.xlsx
```

**Batch:**

```bash
python batch_compare/automate_grouping.py --input comparison_pairs.csv
```

---

## 🔌 Dependencies

Install Python dependencies:

```bash
pip install python-magic pandas openpyxl
```

Install `ffprobe` (optional, for video/media type detection):

* **macOS:**

  ```bash
  brew install ffmpeg
  ```

* **Windows:**
  Install manually via [FFmpeg Downloads](https://ffmpeg.org/download.html) or with Chocolatey:

  ```powershell
  choco install ffmpeg
  ```

---

## 📊 Output Examples

* `rename_log.csv`: all file rename actions
* `undo_log.csv`: supports rollback of changes
* `working_inventory.csv`: full file index
* `spreadsheet_comparison_log.csv`: duplicate/mismatch detection log

---

## 🔮 Future Features

* [ ] YAML-based MIME-extension config
* [ ] ID tagging for individuals and projects
* [ ] Metadata-assisted duplicate detection
* [ ] Zotero/Obsidian integration for academic indexing

---

**Last updated:** August 2025