#!/bin/bash

# ==============================================================================
# 📦 iCloud Drive Backup Script
# ------------------------------------------------------------------------------
# This script backs up your iCloud Drive (~/Library/Mobile Documents/com~apple~CloudDocs/)
# to an external destination folder (default: /Volumes/CrucialX9), using `rsync`.
#
# 💡 USAGE:
#   ./rsync_icloud_exclusion.sh             → Dry run (default, no changes made)
#   ./rsync_icloud_exclusion.sh --real-run  → Performs the actual copy (with confirmation)
#   ./rsync_icloud_exclusion.sh --help      → Show help message
#
# 🛡️ SAFETY FEATURES:
#   - Dry run is the default mode
#   - Real run prompts for confirmation
#   - Excludes unnecessary or sensitive folders
#   - Saves a timestamped log file to your home directory
#
# 🧪 DRY RUN output uses `--itemize-changes` for detailed simulation:
#   Symbols like `>f++++++++` or `cd+++++++` indicate what *would* change:
#     >  = file to be transferred
#     f  = regular file
#     d  = directory
#     +  = creation
#     t  = timestamp change
#     s  = size change
#     .  = no change
#
# 🧰 rsync FLAGS:
#   -a  Archive mode (preserve metadata)
#   -v  Verbose output (list files)
#   -h  Human-readable sizes
#   -n  Dry-run (when DRYRUN=true)
#   --progress  Show copy progress
#   --stats     Show summary
#   --itemize-changes  Show detailed changes (dry run only)
# ==============================================================================

SOURCE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/"
DEST="/Volumes/CrucialX9"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Default to dry run unless overridden
DRYRUN=true

# -----------------------------------------
# Parse CLI Arguments
# -----------------------------------------
case "$1" in
  --real-run)
    DRYRUN=false
    ;;
  --help|-h)
    echo ""
    echo "📦  iCloud Drive Backup Script"
    echo "-------------------------------"
    echo "Usage:"
    echo "  ./rsync_icloud_exclusion.sh             → Dry run (default)"
    echo "  ./rsync_icloud_exclusion.sh --real-run  → Perform live backup (with confirmation)"
    echo "  ./rsync_icloud_exclusion.sh --help      → Show this help message"
    echo ""
    echo "This script uses rsync to safely back up iCloud Drive contents."
    echo "Log file is saved to your home directory: icloud_rsync_<timestamp>.log"
    echo ""
    echo "In DRY RUN mode, file change indicators (from --itemize-changes):"
    echo "  >f++++++++  = new file would be created"
    echo "  >f..t...... = timestamp would change"
    echo "  cd++++++++  = new directory would be created"
    echo ""
    exit 0
    ;;
  "")
    # No argument = dry run
    ;;
  *)
    echo "❌ Unknown option: $1"
    echo "Run with --help to see usage."
    exit 1
    ;;
esac

# -----------------------------------------
# Configure rsync flags and logging
# -----------------------------------------
if [ "$DRYRUN" = true ]; then
  FLAGS="-avhn --progress --stats --itemize-changes"
  LOGFILE=~/icloud_rsync_dryrun_$TIMESTAMP.log
  echo "🧪 DRY RUN: Simulating backup only — no files will be copied."
else
  FLAGS="-avh --progress --stats"
  LOGFILE=~/icloud_rsync_$TIMESTAMP.log
  echo "🚨 LIVE RUN: Files WILL BE COPIED to $DEST"

  # Check that destination is mounted
  if [ ! -d "$DEST" ]; then
    echo "❌ Destination drive not found at: $DEST"
    exit 1
  fi

  echo "⚠️  Are you sure you want to continue with the live backup?"
  read -p "Type 'yes' to proceed: " confirm
  if [[ "$confirm" != "yes" ]]; then
    echo "❌ Backup cancelled."
    exit 1
  fi
fi

# -----------------------------------------
# Run rsync with all exclusions
# -----------------------------------------
sudo caffeinate -i rsync $FLAGS \
  --exclude='~$*' \
  --exclude='.DS_Store' \
  --exclude='._*' \
  --exclude='.Trash*' \
  --exclude='.TemporaryItems' \
  --exclude='.Spotlight-V100' \
  --exclude='*.icloud' \
  --exclude='*.iCloud*' \
  --exclude='*/Icon?' \
  --exclude='*/.DocumentRevisions-V100' \
  --exclude='*/.fseventsd' \
  --exclude='*/.Sync*' \
  --exclude='*/.com.apple.timemachine.supported' \
  --exclude='*/com~apple~CloudDocs/.Trash' \
  --exclude='*/com~apple~CloudDocs/.Trash-*' \
  --exclude='*/Desktop/Waco/*' \
  --exclude='*/bmw i8/*' \
  --exclude='*/Spiff photos/*' \
  --exclude='*/House/*' \
  --exclude='*/portland/*' \
  --exclude='*/John slides/*' \
  --exclude='*/Desktop/Mark/Personal/*' \
  --exclude='*/Desktop/Mark/VB House/*' \
  --exclude='*/Desktop/Mark/Waco/*' \
  --exclude='*Tenure*' \
  --exclude='*Vitae*' \
  --exclude='*Payroll*' \
  --exclude='*LoR*' \
  "$SOURCE" "$DEST" \
  --log-file="$LOGFILE"

# -----------------------------------------
# Wrap-up
# -----------------------------------------
if [ "$DRYRUN" = true ]; then
  echo "✅ Dry run complete. Log saved to: $LOGFILE"
else
  echo "✅ Backup complete. Log saved to: $LOGFILE"
fi

echo "📅 Finished at: $(date)"
