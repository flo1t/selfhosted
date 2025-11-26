# floit - selfhosted

## Teamspeak

### Description


### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/teamspeak | folder for teamspeak |
| ~/docker/teamspeak/.env | env file for secrets |
| ~/docker/teamspeak/teamspeak-compose.yml | docker compose file |
| ~/docker/teamspeak/setup-files | folder for custom files, which are not used from docker |
| ~/docker/teamspeak/data | config folder |
| ~/docker/teamspeak/sql | data folder |

### Setup
#### Overview

#### Prerequisites
- Open ports
- Traefik

#### Setup Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/teamspeak/{data,sql}
touch ~/docker/teamspeak/.env
sudo chmod 600 ~/docker/teamspeak/.env
```

Update all variables in the .env file according to your setup. Some of the variables are generated in a later step.
```sh
nano ~/docker/teamspeak/.env

# add:
TS3SERVER_DB_PASSWORD=<pw>
TS3SERVER_DB_USER=<db user>
TS3SERVER_DB_NAME=<db name>
```

Start the Docker container:
`docker compose -f ~docker/teamspeak/teamspeak-compose.yml up -d`

Add a dns entry to access the teamspeak server if needed.

#### Open Traefik ports
- Go to srv01 and update the traefik-compose.yml file `nano ~/docker/traefik/traefik-compose.yml`
```yml
    ports:
      - 10011:10011 # teamspeak10011
      - 30033:30033 # teamspeak30033
      - 9987:9987/udp # teamspeak9987
...
      - --entryPoints.teamspeak10011.address=:10011/tcp
      - --entryPoints.teamspeak30033.address=:30033/tcp
      - --entryPoints.teamspeak9987.address=:9987/udp
```

#### NAT
If you want to allow access from the internet, forwared ports 10011/tcp, 30033/tcp and 9987/udp to the Traefik host.

#### Enable log rotate
`sudo nano /etc/logrotate.d/teamspeak`
```sh
/home/<username>/docker/teamspeak/data/logs/*.log
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
            docker kill --signal="USR1" teamspeak
        endscript
}
```
Test it: `sudo logrotate -f /etc/logrotate.d/teamspeak --debug`
Optional: Execute it once: `sudo logrotate -f /etc/logrotate.d/teamspeak`

### Maintenance
#### Change serveradmin password
`nano ~/docker/teamspeak/teamspeak-compose.yml`
```yml
TS3SERVER_SERVERADMIN_PASSWORD: "<pw>"
```
Check the logs to see if the password change was successfull `docker logs teamspeak | grep ServerLibPriv`.

#### Recreate admin token
```sh
telnet <ts fqdn> 10011
login client_login_name=serveradmin client_login_password=<pw>
use 1
tokenadd tokentype=0 tokenid1=6 tokenid2=0
```

#### Get admin token
```sh
docker exec -ti teamspeak_db /bin/bash
mariadb --user root -p

show databases;
use teamspeak;
show tables;
select * from tokens;
```

### Monitoring
- Create query user: Login with TS3 client
    - Add ServerQuery User
- Add Telegraf configuration (setup-files/teamspeak.conf): `nano ~/docker/monitoring/telegraf/telegraf.d/teamspeak.conf`