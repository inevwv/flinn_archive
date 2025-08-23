#!/bin/bash

# -----------------------------------------
# iCloud Drive Backup Script via rsync
# -----------------------------------------

SOURCE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/"
DEST="/Volumes/CrucialX9"

# If the script is run with --help or with no arguments, show a help message
if [[ "$1" == "--help" || -z "$1" ]]; then
  echo ""
  echo "📦  iCloud Drive Backup Script (rsync_icloud_exclusion.sh)"
  echo "----------------------------------------------------------"
  echo "Usage:"
  echo "  ./rsync_icloud_exclusion.sh           # Run with built-in DRYRUN toggle"
  echo ""
  echo "What it does:"
  echo "  ✅ Backs up your iCloud Drive to an external volume using rsync"
  echo "  🚫 Skips junk files, system folders, and private or redundant items"
  echo ""
  echo "rsync flags used:"
  echo "  -a   Archive mode (preserves permissions, symlinks, timestamps)"
  echo "  -v   Verbose output (shows all files being considered)"
  echo "  -h   Human-readable sizes"
  echo "  -n   DRY RUN mode (simulate only, no copying)"
  echo "  --progress  Show progress bar during copying"
  echo "  --stats     Show summary at the end"
  echo ""
  echo "🧪 DRYRUN is controlled from inside the script:"
  echo "     DRYRUN=true   ← simulate"
  echo "     DRYRUN=false  ← real copy (with confirmation)"
  echo ""
  echo "🚨 Real runs will prompt you before doing anything."
  echo "📝 Log file is saved to: ~/icloud_rsync.log"
  echo ""
  echo "🔧 Tip: If you see a permission error, run:"
  echo "     chmod +x ./rsync_icloud_exclusion.sh"
  exit 0
fi

# -----------------------------------------
# DRY RUN TOGGLE
# Set to true to simulate the sync without copying
# -----------------------------------------
DRYRUN=false  # ← change this to true for testing

# Set rsync flags based on dry run
if [ "$DRYRUN" = true ]; then
  FLAGS="-avhn"
  echo "🧪 DRY RUN: No files will be copied to $DEST"
else
  FLAGS="-avh"
  echo "🚨 LIVE RUN: Files WILL BE COPIED to $DEST"
  
  # 🔒 Confirmation prompt
  echo "⚠️  You are about to run a LIVE BACKUP to: $DEST"
  read -p "Do you want to continue? (y/N): " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "❌ Backup cancelled by user."
    exit 1
  fi
fi

# -----------------------------------------
# Perform the rsync backup
# -----------------------------------------

sudo caffeinate -i rsync $FLAGS --progress --stats \
  \
  # Exclude temporary or system-specific files
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
  # Exclude specific folders by path
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
  # Exclude files/folders by name content
  --exclude='*Tenure*' \
  --exclude='*Vitae*' \
  --exclude='*Payroll*' \
  --exclude='*LoR*' \
  \
  "$SOURCE" "$DEST" \
  --log-file=~/icloud_rsync.log


# -----------------------------------------
# End
# -----------------------------------------
if [ "$DRYRUN" = true ]; then
  echo "🧪 Dry run complete. Check ~/icloud_rsync.log for the full simulation."
else
  echo "✅ Backup complete. Log saved to ~/icloud_rsync.log"
fi

