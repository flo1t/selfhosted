# floit - selfhosted

## Code-Server

### Description
Run VS Code on any machine anywhere and access it in the browser.
https://github.com/coder/code-server

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/code-server | folder for code-server |
| ~/docker/code-server/.env | env file for secrets |
| ~/docker/code-server/code-server-compose.yml | docker compose file |
| ~/docker/code-server/config | data folder |

### Setup
#### Prerequisites
- Traefik
- Authentik

#### Setup Docker container
Prepare the folder structure:
`mkdir -p ~/docker/code-server/config` 

Update the variables in the .env file according to your setup:
```sh
nano ~/docker/code-server/.env

# add:
PUID=<user id>
PGID=<group id>
TZ=Europe/Zurich
FQDN=<fqdn>
```

Start the Docker container:
`docker compose -f ~docker/code-server/code-server-compose.yml up -d`

Don't forget to add and dns entry for the service.

### Connect to Gitea-Repository
- Open code-server and start a terminal (can be done via menu -> terminal)
- Create a SSH key: `ssh-keygen -t ed25519`
- Copy the pubkey: `cat ~/.ssh/id_ed25519.pub`
- Go to Gitea nad navigate to User -> Settings -> SSH -> "Add key"
- Verify the key with the given command in the code-server terminal (adjust the location to ~/.ssh/id_ed25519)
- Copy the Gitea Repository SSH URL
- Go to code-server and press F1 -> Clone
- Enter the URL and follow the wizard
