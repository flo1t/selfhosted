#!/bin/bash
. $(dirname "$0")/.env

# TARGET_FOLDER, SOURCE_FOLDER and DISCORD_URL are set in the .env file
source_folder=$SOURCE_FOLDER
target_folder=$TARGET_FOLDER
discord_url=$DISCORD_BACKUP_URL

current_date=$(date +"%Y-%m-%d")
mkdir -p "${target_folder}"

backup_folder="${target_folder}/${current_date}"
docker_backup_folder="${backup_folder}/docker"

# Funktion zum Stoppen der Docker-Container
stop_containers() {
    echo "Stopping containers for $1"
    docker compose -f "$1" stop
}

# Funktion zum Starten der Docker-Container
start_containers() {
    echo "Starting containers for $1"
    docker compose -f "$1" up -d
}

# Erstelle das Docker-Backup-Verzeichnis
mkdir -p "$docker_backup_folder"

# Kopiere Daten und stoppe/start Docker-Container für jedes Unterverzeichnis in $source_folder/docker
for dir in $(find "$source_folder/docker" -maxdepth 1 -type d); do
    compose_file=$(find "$dir" -maxdepth 1 -name "*-compose.yml")
    if [ -n "$compose_file" ]; then
        stop_containers "$compose_file"
        rsync -av --delete --link-dest="${target_folder}/latest/docker/$(basename $dir)" "$dir/" "${docker_backup_folder}/$(basename $dir)/"
        start_containers "$compose_file"
    fi
done

# Kopiere die restlichen Daten
rsync -av --delete --exclude="docker" --link-dest="${target_folder}/latest" "${source_folder}/" "${backup_folder}/"

# Überprüfe, ob rsync erfolgreich war
if [ $? -eq 0 ]; then
    rm -rf "${target_folder}/latest"
    ln -s "${backup_folder}" "${target_folder}/latest"

    backup_dirs=($(ls -d -1 "${target_folder}"/* | sort))
    num_backups=${#backup_dirs[@]}

    if [ $num_backups -gt 3 ]; then
        to_delete=$((num_backups - 3))
        for ((i = 0; i < to_delete; i++)); do
            rm -rf "${backup_dirs[i]}"
        done
    fi

    backup_status="Backup $(hostname) successful"
else
    backup_status="Backup $(hostname) failed"
fi

# Meldung via Discord
echo "{\"content\":\"${backup_status}\"}" | curl -H "Content-Type: application/json" -d @- "$discord_url"