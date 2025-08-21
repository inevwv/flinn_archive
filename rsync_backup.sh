#!/bin/bash

# Define source and target
SOURCE="/Volumes/[INSERTNAME]"
DEST="/Volumes/CrucialX9"

# Do the copy with good excludes
rsync -avh --progress --stats \
  --exclude='~$*' \
  --exclude='.DS_Store' \
  --exclude='._*' \
  --exclude='.Spotlight-V100' \
  --exclude='.Trashes' \
  --exclude='.TemporaryItems' \
  "$SOURCE" "$DEST"

# 1. chmod +x ~/rsync_backup.sh <-- makes executable
# 2. sudo caffeinate -i ~/rsync_backup.sh <--let's run overnight
