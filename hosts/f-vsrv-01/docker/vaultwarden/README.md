# floit - selfhosted

## Vaultwarden

### Description
An alternative server implementation of the Bitwarden Client API, written in Rust and compatible with official Bitwarden clients, perfect for self-hosted deployment where running the official resource-heavy service might not be ideal.
https://github.com/dani-garcia/vaultwarden

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/vaultwarden | folder for vaultwarden |
| ~/docker/vaultwarden/.env | env file for secrets |
| ~/docker/vaultwarden/vaultwarden-compose.yml | docker compose file |
| ~/docker/vaultwarden/data | data folder |
| ~/docker/vaultwarden/logs | logs folder |

### Setup
#### Overview

#### Prerequisites

#### Setup Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/vaultwarden/{logs, data}
touch ~/docker/vaultwarden/.env
sudo chmod 600 ~/docker/vaultwarden/.env
```

Update all variables in the .env file according to your setup.
```sh
nano ~/docker/vaultwarden/.env

# add:
FQDN=<FQDN>

# Mail
SMTP_PASSWORD="<PW>"
SMTP_USERNAME="<USERNAME>"
SMTP_FROM="<SENDER>"
SMTP_HOST="<SERVER>"
```

Don't forget to add the needed DNS entry (vault.domain) for reaching the service.

Start the Docker container:
`docker compose -f ~docker/vaultwarden/vaultwarden-compose.yml up -d`

#### Setup Logrotation on the Docker host
`sudo nano /etc/logrotate.d/vaultwarden`
```
/home/<username>/docker/vaultwarden/logs/*.log
{
        su root root
        daily
        maxsize 20M
        rotate 14
        missingok
        compress
        notifempty
        dateext
        dateformat -%Y%m%d%H
        postrotate
            docker kill --signal="USR1" vaultwarden
        endscript
}
```

Test it: `sudo logrotate -f /etc/logrotate.d/vaultwarden --debug`
Optional: Execute it once: `sudo logrotate -f /etc/logrotate.d/vaultwarden`

## ToDo
- Finish this README page