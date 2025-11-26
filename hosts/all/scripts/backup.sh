#!/bin/bash
. $(dirname "$0")/.env

# TARGET_FOLDER, SOURCE_FOLDER and DISCORD_URL are set in the .env file
source_folder=$SOURCE_FOLDER
target_folder=$TARGET_FOLDER
#compressed_target_folder=$COMPRESSED_TARGET_FOLDER
discord_url=$DISCORD_BACKUP_URL
eclude_docker_folders=$EXCLUDE_DOCKER_FOLDERS

mkdir -p "${target_folder}"

backup_folder="${target_folder}"
docker_backup_folder="${backup_folder}/docker"

# Function to stop Docker containers
stop_containers() {
    echo "Stopping containers for $1"
    docker compose -f "$1" stop
}

# Function to start Docker containers
start_containers() {
    echo "Starting containers for $1"
    docker compose -f "$1" up -d
}

# Create Docker backup directory
mkdir -p "$docker_backup_folder"

# Copy data and stop/start Docker containers for each subdirectory in $source_folder/docker
for dir in $(find "$source_folder/docker" -maxdepth 1 -type d); do
    compose_file=$(find "$dir" -maxdepth 1 -name "*-compose.yml")
    if [ -n "$compose_file" ]; then
        stop_containers "$compose_file"
        echo "Copying data from $dir to $docker_backup_folder"

        exclude_params=()
        dir_name=$(basename "$dir")
        # Check if excludes are defined for this folder
        if [[ -n "${EXCLUDE_DOCKER_FOLDERS[$dir_name]:-}" ]]; then
            for exclude_path in ${EXCLUDE_DOCKER_FOLDERS[$dir_name]}; do
                exclude_params+=(--exclude="$exclude_path")
            done
        fi

        if [ ${#exclude_params[@]} -gt 0 ]; then
            rsync -av --delete "${exclude_params[@]}" "$dir/" "${docker_backup_folder}/$dir_name/"
        else
            rsync -av --delete "$dir/" "${docker_backup_folder}/$dir_name/"
        fi
        start_containers "$compose_file"
    fi
done

# Copy remaining data except the docker and excluded folders
exclude_params=()
exclude_params+=(--exclude="/docker")
if [[ -n "${EXCLUDE_FOLDERS:-}" ]]; then
    # If EXCLUDE_FOLDERS is an indexed array, iterate it directly
    for val in "${EXCLUDE_FOLDERS[@]}"; do
        exclude_params+=(--exclude="$val")
    done
fi

echo "Copying data from $source_folder to $backup_folder"
rsync -av --delete "${exclude_params[@]}" "${source_folder}/" "${backup_folder}/"

# Check if rsync was successful
if [ $? -eq 0 ]; then
    backup_status="Backup $(hostname) successful"
else
    backup_status="Backup $(hostname) failed"
fi

# Send notification via Discord
echo "{\"content\":\"${backup_status}\"}" | curl -H "Content-Type: application/json" -d @- "$discord_url"