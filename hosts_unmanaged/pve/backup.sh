#!/bin/bash
. $(dirname "$0")/.env

discord_url=$DISCORD_BACKUP_URL

export PBS_REPOSITORY=$PBS_REPOSITORY
export PBS_PASSWORD=$PBS_PASSWORD
export PBS_ENCRYPTION_PASSWORD=$PBS_ENCRYPTION_PASSWORD

proxmox-backup-client backup data-share.pxar:/data/share data-backup-rsync.pxar:/data/backup/rsync --change-detection-mode=metadata --crypt-mode=encrypt
proxmox-backup-client prune host/pve --keep-daily 5

if [ $? -ne 0 ]; then
    backup_status="File backup $(hostname) failed"
else
    backup_status="File backup $(hostname) successful"
fi

export PBS_REPOSITORY=
export PBS_PASSWORD=
export PBS_ENCRYPTION_PASSWORD=

# Notification via Discord successfull or not
echo "{\"content\":\"${backup_status}\"}" | curl -H "Content-Type: application/json" -d @- "$discord_url"
