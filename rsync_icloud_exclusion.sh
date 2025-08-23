#!/bin/bash

# -----------------------------------------
# iCloud Drive Backup Script via rsync
# -----------------------------------------

SOURCE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/"
DEST="/Volumes/CrucialX9"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# -----------------------------------------
# Default to dry run unless overridden
# -----------------------------------------
DRYRUN=true

case "$1" in
  --real-run)
    DRYRUN=false
    ;;
  --help|-h)
    echo ""
    echo "📦  iCloud Drive Backup Script"
    echo "-------------------------------"
    echo "Usage:"
    echo "  ./rsync_icloud_exclusion.sh             # Dry run (default)"
    echo "  ./rsync_icloud_exclusion.sh --real-run  # Perform live backup (with confirmation)"
    echo "  ./rsync_icloud_exclusion.sh --help      # Show this help message"
    echo ""
    echo "Log file will be saved to: ~/icloud_rsync_<timestamp>.log"
    echo ""
    exit 0
    ;;
  "" )
    # No argument = dry run (default)
    ;;
  *)
    echo "❌ Unknown option: $1"
    echo "Run with --help to see usage."
    exit 1
    ;;
esac

# -----------------------------------------
# Configure run mode
# -----------------------------------------

if [ "$DRYRUN" = true ]; then
  FLAGS="-avhn"
  LOGFILE=~/icloud_rsync_dryrun_$TIMESTAMP.log
  echo "🧪 DRY RUN: No files will be copied."
else
  FLAGS="-avh"
  LOGFILE=~/icloud_rsync_$TIMESTAMP.log
  echo "🚨 LIVE RUN: Files WILL BE COPIED to $DEST"

  # Check that destination is mounted
  if [ ! -d "$DEST" ]; then
    echo "❌ Destination drive not found at $DEST"
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
# Perform the rsync backup
# -----------------------------------------

sudo caffeinate -i rsync $FLAGS --progress --stats \
  \
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
  \
  --exclude='*/Desktop/Waco/*' \
  --exclude='*/bmw i8/*' \
  --exclude='*/Spiff photos/*' \
  --exclude='*/House/*' \
  --exclude='*/portland/*' \
  --exclude='*/John slides/*' \
  --exclude='*/Desktop/Mark/Personal/*' \
  --exclude='*/Desktop/Mark/VB House/*' \
  --exclude='*/Desktop/Mark/Waco/*' \
  \
  --exclude='*Tenure*' \
  --exclude='*Vitae*' \
  --exclude='*Payroll*' \
  --exclude='*LoR*' \
  \
  "$SOURCE" "$DEST" \
  --log-file="$LOGFILE"

# -----------------------------------------
# Wrap-up message
# -----------------------------------------
if [ "$DRYRUN" = true ]; then
  echo "✅ Dry run complete. Log saved to: $LOGFILE"
else
  echo "✅ Backup complete. Log saved to: $LOGFILE"
fi

echo "📅 Finished at: $(date)"
