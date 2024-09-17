# floit - selfhosted

## CrowdSec

### Description
CrowdSec is a free, modern & collaborative behavior detection engine, coupled with a global IP reputation network. It stacks on fail2ban's philosophy but is IPV6 compatible and 60x faster (Go vs Python), it uses Grok patterns to parse logs and YAML scenarios to identify behaviors. CrowdSec is engineered for modern Cloud / Containers / VM-based infrastructures (by decoupling detection and remediation).
https://www.crowdsec.net/

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/crowdsec | folder for crowdsec |
| ~/docker/crowdsec/.env | env file for secrets |
| ~/docker/crowdsec/crowdsec-compose.yml | docker compose file |
| ~/docker/crowdsec/setup-files | folder for custom files, which are not used from docker |
| ~/docker/crowdsec/config | config folder |
| ~/docker/crowdsec/data | data folder |
| ~/docker/crowdsec/cloudflare-bouncer | cloudflare-bouncer data |
| ~/docker/crowdsec/sql | db folder |
| ~/docker/crowdsec/logs | logs folder |

### Setup
#### Overview
SRV01 is the main server in my setup. CrowdSec consists of different components: The agent to parse logs and contacting the local or remote API for decisions, the local API (only enabled on srv01), the bouncers, which are executing the decisions and finally the CrowdSec CLI. The agents don't use their local API and are connected to the main server for decisions.
I'm using the following bouncers:
- Traefik bouncer (srv01)
- Cloudflare bouncer (srv01)
- Firewall bouncer (per host)
- Wordpress bouncer (within the wordpress installation)

As all traffic is routed through Traefik in my setup, some of the bouncers (e.g. firewall bouncer) on the agents seems useless. But those bouncers are just working, when the service is accessed via FQDN and not via IP and it also doesn't work for non http rules. Because of that it could make sense to add them to your agents as well.

I had to change the default port 8080 because of other services to 8082.

If you have problems starting the container, exclude the bouncers for the first start and add them later.

#### Prerequisites
- Traefik setup
- Cloudflare API key with the following permissions:
    - Account: Account Filter Lists: Edit
    - Account: Account Firewall Access Rules: Edit
    - Zone: Zone: Read
    - Zone: Firewall Services: Edit
    - Account Resources: Include: All accounts (optional to ban ips on all resources)
    - Zone Resources: Include: All zones (optional to ban ip on all zones)

#### Setup Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/crowdsec/{config,data,cloudflare-bouncer,sql,logs}
touch ~/docker/crowdsec/.env
```

Update all variables in the .env file according to your setup. Some of the variables are generated in a later step.
```sh
nano ~/docker/crowdsec/.env

# add:
TRAEFIK_BOUNCER_KEY=<Traefik Bouncer Key>
MYSQL_DB=<DB Name>
MYSQL_PASSWORD=<DB Password>
HOSTNAME=<HOSTNAME>
```

Start the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d`

#### Change to DB after the first start
After the first start of the containers, you can switch from SQLite to mariadb:
`sudo nano ~/docker/crowdsec/config/config.yaml`
```yaml
common:
  log_media: file
...
db_config:
  type: mysql
  user: <username>
  password: <db password>
  db_name: <db name>
  host: <db container-name>
  port: 3306
  use_wal: false
```

Restart the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d --force-recreate`

#### Collections
Modify the collections variable in the 'crowdsec-compose.yml' files to suit your needs. Collections can be found here: https://app.crowdsec.net/hub/collections.
Add a crontab job, to upgrade the update the collections every hour:
`crontab -e`
`0 * * * * docker exec crowdsec cscli hub update && docker exec crowdsec cscli hub upgrade`

Restart the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d --force-recreate`

#### Enroll instance to CrowdSec
1. Go to https://app.crowdsec.net and create an account
2. Go to enroll instance and enter the command on the main server

Restart the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d --force-recreate`

#### Add Traefik bouncer
Generate an API-Key:
`docker exec -t crowdsec cscli bouncers add crowdsec-bouncer-traefik`

Add the generated key to "~/docker/crowdsec/.env" (TRAEFIK_BOUNCER_KEY).

Restart the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d --force-recreate`

Don't forget to add a Traefik middleware and append it to your middleware chains. The middleware is visible in the traefik configuration folder here on GitHub.
You also have to add the crowdsec network to the Traefik compose file and restart traefik afterwards:
```yml
...
  crowdsec:
    external: true
```

#### Add Cloudflare bouncer
Generate an API-Key:
`docker exec -ti crowdsec cscli bouncers add crowdsec-bouncer-cloudflare`

Add Cloudflare API-Token to bouncer:
`docker run crowdsecurity/cloudflare-bouncer -g <API-Token> > ~/docker/crowdsec/cloudflare-bouncer/cfg.yaml`

Check if the LAPI_URL is correct and add the Crowdsec Bouncer API-Key from the first step to the config:
`nano ~/docker/crowdsec/cloudflare-bouncer/cfg.yaml`
```
crowdsec_lapi_url: http://crowdsec:8080/
crowdsec_lapi_key: <API-KEY>
```

Restart the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d --force-recreate`

### General Settings
#### Ban duration
I've set the ban duration to 72h:
`sudo nano ~/docker/crowdsec/config/profiles.yaml`
`   duration: 72h`

#### Enable Notifications
Add the configuration form setup-files/http.yml to `sudo nano ~/docker/crowdsec/config/notifications/http.yaml` to enable notifications via Discord (replace <Discord URL> with the webhook URL).

### Useful commands
#### Check if the configuration is working
`docker exec crowdsec cscli metrics`

#### Show / Remove IP from decisions
`docker exec crowdsec cscli decisions list`
`docker exec crowdsec cscli decisions delete -i <IP>`

### ToDo
- Do something with the crowdsec metrics