# floit - selfhosted

## Authentik - Outpost

### Description
authentik is an open-source Identity Provider that emphasizes flexibility and versatility, with support for a wide set of protocols.
https://goauthentik.io/

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/authentik | folder for Authentik |
| ~/docker/authentik/.env | env file for secrets |
| ~/docker/authentik/authentik-compose.yml | docker compose file |

### Setup

#### Prerequisites
- Running Authentik installation
- Token of the Authentik Outpost (https://docs.goauthentik.io/docs/add-secure-apps/outposts/)
-- Press "View Deployment Info" to retrieve the token from the Proxy Outpost (don't select Docker integration)
- The Outpost must be connected to the traefik network

#### Setup Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/authentik
touch ~/docker/authentik/.env
sudo chmod 600 ~/docker/authentik/.env
```

Update the variables in the .env file according to your setup:
```sh
nano ~/docker/authentik/.env

# add:
AUTHENTIK_FQDN=<Authentik HOST + DOMAIN>
AUTHENTIK_TOKEN='<AUTHENTHIK TOKEN>'

HOST=<Authentik HOST>
DOMAIN=<Authentik DOMAIN>
```

#### Various settings
- Add traefik authentik middleware

### ToDo

