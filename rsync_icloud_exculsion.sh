#!/bin/bash

SOURCE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/"
DEST="/Volumes/MyBackupDisk/iCloudBackup/"

# # Rename anth* folders to "Anthropology"
# find "$SOURCE" -type d -iname 'anth*' | while read -r dir; do
#   parent="$(dirname "$dir")"
#   newname="$parent/Anthropology"
#   if [[ "$dir" != "$newname" ]]; then
#     echo "Renaming: $dir → $newname"
#     mv "$dir" "$newname"
#   fi
# done

# Perform the rsync copy with exclusions
sudo caffeinate -i rsync -avh --progress --stats \
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

  # Exclude by filename contents
  --exclude='*Tenure*' \
  --exclude='*Vitae*' \
  --exclude='*Payroll*' \
  --exclude='*LoR*' \

  
  "$SOURCE" "$DEST" \
  --log-file=~/icloud_rsync.log


many redundancies b/w /emotions/ and /desktop/emotions/


—> to consolidate teaching material folders

in inventory check for duplicate file names
