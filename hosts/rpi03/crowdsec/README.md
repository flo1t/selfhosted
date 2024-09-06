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
| ~/docker/crowdsec/setup files | folder for custom files, which are not used from docker |
| ~/docker/crowdsec/config | config folder |
| ~/docker/crowdsec/data | data folder |

### Setup
#### Overview
SRV01 is the main server in my setup. CrowdSec consists of different components: The agent to parse logs and contacting the local or remote API for decisions, the local API (only enabled on srv01), the bouncers, which are executing the decisions and finally the CrowdSec CLI. The agents don't use their local API and are connected to the main server for decisions.
I'm using the following bouncers:
- Traefik bouncer (srv01)
- Cloudflare bouncer (srv01)
- Firewall bouncer (per host)
- Wordpress bouncer (within the wordpress installation)

As all traffic is routed through Traefik in my setup, some of the bouncers (e.g. firewall bouncer) on the agents seems useless. But those bouncers are just working, when the service is accessed via FQDN and not via IP and it also doesn't work for non http rules. Because of that it could make sense to add them to your agents as well.

If you have problems starting the container, exclude the bouncers for the first start and add them later.

#### Prerequisites
- Crowdsec master installed and configured

#### Setup Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/crowdsec/{config,data}
touch ~/docker/crowdsec/.env
```

Update all variables in the .env file according to your setup. Some of the variables are generated in a later step.
```sh
nano ~/docker/crowdsec/.env

# add:
LOCAL_API_IP=<host ip of crowdsec master>
CROWDSEC_AGENT_PASSWORD=<crowdsec agent password>
HOSTNAME=<hostname>
```

Start the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d`

#### Collections
Modify the collections variable in the 'crowdsec-compose.yml' files to suit your needs. Collections can be found here: https://app.crowdsec.net/hub/collections.
Add a crontab job, to upgrade the update the collections every hour:
`crontab -e`
`0 * * * * docker exec crowdsec cscli hub update && docker exec crowdsec cscli hub upgrade`

If you have added more collections, don't forget to mount the volume with the needed log files to the Docker container and update the acquis.yaml file (`sudo nano ~/docker/crowdsec/config/acquis.yaml`).

Restart the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d --force-recreate`

#### Connect to master server
- Run on the agent `docker exec -t crowdsec cscli lapi register -u <host ip of crowdsec master>:8082 --machine <hostname>`
- Run on the master `docker exec -t crowdsec cscli machines validate <hostname>`
- Check if the installation was successful (on the master) `docker exec -t crowdsec cscli machines list`
- If so, add the CROWDSEC_AGENT_PASSWORD from "~/docker/crowdsec/config/local_api_credentials.yaml" to "~/docker/crowdsec/.env"

Restart the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d --force-recreate`

#### Add the firewall bouncer to the host
This steps have to be done on the host itself:
```sh
curl -s https://packagecloud.io/install/repositories/crowdsec/crowdsec/script.deb.sh | sudo bash
sudo apt update
sudo apt install crowdsec-firewall-bouncer-iptables
```

On the master:
`docker exec -t crowdsec cscli bouncers add bouncer-firewall-<hostname>`

On the agent again:
`sudo nano /etc/crowdsec/bouncers/crowdsec-firewall-bouncer.yaml`
```yaml
...
log_max_size: 10 # limit log file to 10 mb
...
api_url: http://<host ip of crowdsec master>:8082
api_key: <add the API key from the command above>
disable_ipv6: true
deny_log: true
iptables_chains:
   - INPUT
#  - FORWARD
   - DOCKER-USER
...
```

`sudo systemctl restart crowdsec-firewall-bouncer.service`

Verify successful installation:
- On the agent: `sudo tail -f /var/log/kern.log | grep crowdsec`
- or `sudo cat /var/log/crowdsec-firewall-bouncer.log`
- On the master: `docker exec -t crowdsec cscli bouncers list`