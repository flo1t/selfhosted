# floit - selfhosted

## Jellyfin

### Description
Jellyfin is a Free Software Media System that puts you in control of managing and streaming your media. It is an alternative to the proprietary Emby and Plex, to provide media from a dedicated server to end-user devices via multiple apps.
https://jellyfin.org/

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/jellyfin | folder for jellyfin |
| ~/docker/jellyfin/.env | env file for secrets |
| ~/docker/jellyfin/jellyfin-compose.yml | docker compose file |
| ~/docker/jellyfin/setup-files | folder for custom files, which are not used from docker |
| ~/docker/jellyfin/config | data folder |
| ~/docker/jellyfin/web-config | folder for web config |

### Setup
#### Overview
I'm mounting a NFS share from my NAS to /mnt/media. This folder will be used as Jellyfin media location.

#### Prerequisites
- Running Traefik installation

#### Mount NFS share
```sh
sudo apt-get update
sudo apt-get install nfs-common -y
sudo mkdir -p /mnt/media
sudo nano /etc/fstab
```

Add this line to the end of the file:
`<NAS IP>:/<NAS volume>/<shared folder> /mnt/media nfs4 defaults,noatime,x-systemd.automount,x-systemd.idle-timeout=60 0 0`

#### Setup Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/jellyfin/{config,web-config}
touch ~/docker/jellyfin/web-config/config.json
touch ~/docker/jellyfin/.env
sudo chmod 600 ~/docker/jellyfin/.env
```

Update the variables in the .env file according to your setup:
```sh
nano ~/docker/jellyfin/.env

# add:
FQDN=<Jellyfin URL>
TZ=Europe/Zurich
```

Execute this command to retrieve the "group_add" value, which has to be replaced in the jellyfin-compose.yml file (needed for hardware transcoding).
`getent group render | cut -d: -f3`

Start the Docker container:
`docker compose -f ~docker/jellyfin/jellyfin-compose.yml up -d`

Don't forget to set needed DNS entries for reaching the service.

#### Hardware transcoding
Check the supported profiles with this command:
`/usr/lib/jellyfin-ffmpeg/vainfo --display drm --device /dev/dri/renderD128`

Enable hardware transcoding via webinterface (this settings are based on your hardware, adjust it to your needs):
- Navigate via the Administration Dashboard to Playback -> Transcoding
    - Select the hardware acceleration type: Intel QuickSync (QSV) in my case
    - Check every codec except AV1 (retrieved via the supported profiles command above)
    - Check "Allow encoding in HEVC format"
    - Check "Enable VPP Tone mapping"

#### Cloudflare settings
If you are using Cloudflare, follow the following steps:
- Create a Cloudflare page rule to disable Caching & Performance
    - Rules -> Page rules -> FQDN/* -> Cache lvel: Bypass & Disable performance

#### Various settings
- Allow the determinination of the real IP from clients:
    - Set known proxies under Networking -> Known proxies to:
        - All Cloudflare IPs https://www.cloudflare.com/ips-v4 (if you are using Cloudflare)
        - The IP address of your reverse proxy
        - The Docker network of your Jellyfin container
- Enable Notifications
    - Install the plugin "Webhook" via the Plugins Catalog
        - Add the Destination (Discord in my case)
        - Insert the content from setup-files\discord-notification-template.md to the Template section
- Add menu links to the webinterface:
    - `nano ~/docker/jellyfin/web-config/web-config.json`
    - Add menu points under "menuLinks" like that:
    ```
    {
      "name": "Request Movies/Shows",
      "icon": "download",
      "url": "https://jellyserr.domain"
    },
    ```

### Monitoring
I'm monitoring Jellyfin with Grafana, Telegraf and InfluxDB (flux). RPI01 is my monitoring server.
- Create a Jellyfin API Token via webinterface
- Add a custom telegraf config:
    - Switch to your monitoring server
    - Create a new conf file with the content of setup-files\jellyfin-monitoring.conf `nano docker/monitoring/telegraf/telegraf.d/jellyfin.conf`
        - Replace <FQDN> with your fqdn and <Token> with the Jellyfin API token
- Create Grafana Dasboards
    - Time series graph with the active streams: setup-files\grafana-visualization-active-stream-count.json
    - State timeline with streamed files per user: setup-files\grafana-visualization-streams-per-user.json
    - Network throughput: setup-files\grafana-visualization-streams-per-user.json

### Stop simultaneous streams
I made a script (setup-files\stop-jeyllfin-streams.py), to stop simultaneous streams and notify the user about it. The script is run via scheduled Gitea Action.

### ToDo
- Implement Authentik for Jellyserr
- Move Grafana dashboards to Grafana folder as soon as Grafana is published