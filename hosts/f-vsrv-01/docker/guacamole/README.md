# floit - selfhosted

## Apache Guacamole

### Description
Apache Guacamole is a clientless remote desktop gateway. It supports standard protocols like VNC, RDP, and SSH.

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/guacamole | folder for guacamole |
| ~/docker/guacamole/.env | env file for secrets |
| ~/docker/guacamole/guacamole-compose.yml | docker compose file |
| ~/docker/guacamole/drive | drive folder |
| ~/docker/guacamole/record | record folder |
| ~/docker/guacamole/db | db folder |
| ~/docker/guacamole/init | db init script folder |

### Technical aspects
A typical Docker deployment of Guacamole will involve three separate containers, connected over the network:
- **guacamole/guacd**: Provides the guacd daemon, built from the released guacamole-server source with support for VNC, RDP, SSH, telnet, and Kubernetes.
- **guacamole/guacamole**: Provides the Guacamole web application running within Tomcat 9.x with support for WebSocket. The configuration necessary to connect to guacd, MySQL, PostgreSQL, LDAP, etc. will be read automatically from environment variables when the image starts.
- **mysql or postgresql**: Provides the database that Guacamole will use for authentication and storage of connection configuration data.

### Setup
I'm using Authentik as SSO solution and Traefik as reverse proxy.

#### Prerequisites
- Traefik setup
- Authentik setup

#### Prepare Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/guacamole/{drive,record,db,init,config}
touch ~/docker/guacamole/.env
sudo chmod 600 ~/docker/guacamole/.env
sudo chown -R 1001:1001 ~/docker/guacamole/logs
```

#### Pull the db init script
`docker run --rm guacamole/guacamole:latest /opt/guacamole/bin/initdb.sh --postgresql > ./docker/guacamole/init/initdb.sql`

#### Crowdsec
Enable logging via logback.xml file:
`nano ~/docker/guacamole/config/logback.xml`

Add the collection to crowdsec:
`... corvese/apache-guacamole ...`

Add the log dir as volume to crowdsec:
`- ../guacamole/logs:/var/log/guacamole/logs:ro`

Update acquis.yml:
```
---
filenames:
  - /var/log/vaultwarden/logs/apache-guacamole.log
labels:
  type: apache-guacamole

```

##### Enable logrotate
`sudo nano /etc/logrotate.d/guacamole`
```sh
/home/floit/docker/guacamole/logs/*.log
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
            docker kill --signal="USR1" guacamole
        endscript
}
```

Test it: `sudo logrotate -f /etc/logrotate.d/guacamole --debug`
Optional: Execute it once: `sudo logrotate -f /etc/logrotate.d/guacamole`

#### Authentik
I'm using Authentik as identity provider. To implement it, follow the official Lobechat Authentik guide: https://integrations.goauthentik.io/infrastructure/apache-guacamole/ .

Start the Docker container:
`docker compose -f ~docker/guacamole/guacamole-compose.yml up -d`

#### Update .env file
Update all variables in the .env file according to your setup. Some of the variables are generated in a later step.

Start the Docker container:
`docker compose -f ~docker/crowdsec/crowdsec-compose.yml up -d --force-recreate`

### General Settings
#### First start / Default credentials
The first login has to be done with the default credentials: guacadmin - guacadmin.

#### Add servers

### ToDo
- Implement "Add servers" to this readme