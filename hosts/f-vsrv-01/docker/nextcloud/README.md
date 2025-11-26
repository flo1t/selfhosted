# floit - selfhosted

## Nextcloud

### Description
Nextcloud Files is a cloud storage and file sharing software that provides easy access to sharing and collaboration from anywhere, anytime. All that without any data leaks to third parties and with full control over the data.
https://github.com/nextcloud

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/nextcloud | folder for nextcloud |
| ~/docker/nextcloud/.env | env file for secrets |
| ~/docker/nextcloud/nextcloud-compose.yml | docker compose file |

### Setup

#### Prerequisites

#### Setup Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/nextcloud
touch ~/docker/nextcloud/.env
sudo chmod 600 ~/docker/nextcloud/.env
```

Update the variables in the .env file according to your setup:
```sh
nano ~/docker/nextcloud/.env

# add:
...
```

#### Various settings
##### Add cronjob
``sudo crontab -e`

```
*/5 * * * * docker exec -u www-data nextcloud php /var/www/html/cron.php
```

##### Change Logging and trashbin/retentions
`sudo nano ~/docker/nextcloud/nextcloud/config/config.php`

```
...
  'log_type' => 'file',
  'logfile' => '/var/log/nextcloud.log',
...
  'trashbin_retention_obligation' => 'auto,30',
  'versions_retention_obligation' => 'auto,30',
...
```

#### Enable log rotation on the docker host
`sudo nano /etc/logrotate.d/nextcloud`

```
/home/floit/docker/nextcloud/logs/*.log
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
            docker kill --signal="USR1" nextcloud
        endscript
}
/home/floit/docker/nextcloud/logs/apache2/*.log
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
            docker kill --signal="USR1" nextcloud
        endscript
}
```

Test it: `sudo logrotate -f /etc/logrotate.d/nextcloud --debug`
Optional: Execute it once: `sudo logrotate -f /etc/nextcloud.d/vaultwarden`

#### Add Cloudflare proxies and other settings
```
# add cloudflare trusted ips
docker exec --user www-data nextcloud php occ config:system:set trusted_domains 0 --value <nextcloud fqdn>
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 2 --value 173.245.48.0/20
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 3 --value 103.21.244.0/22
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 4 --value 103.22.200.0/22
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 5 --value 103.31.4.0/22
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 6 --value 141.101.64.0/18
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 7 --value 108.162.192.0/18
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 8 --value 190.93.240.0/20
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 9 --value 188.114.96.0/20
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 10 --value 197.234.240.0/22
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 11 --value 198.41.128.0/17
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 12 --value 162.158.0.0/15
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 13 --value 104.16.0.0/13
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 14 --value 104.24.0.0/14
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 15 --value 172.64.0.0/13
docker exec --user www-data nextcloud php occ config:system:set trusted_proxies 16 --value 131.0.72.0/22

docker exec --user www-data nextcloud php occ config:system:set default_phone_region --value="CH"
```

### Operation
#### Reindex all files
`docker exec --user www-data nextcloud php ./occ files:scan --all`

#### Update/Reindex database
```
docker stop nextcloud
docker exec -ti nextcloud-db bash
psql -U <db user> -d nextcloud
ALTER DATABASE nextcloud REFRESH COLLATION VERSION;
REINDEX DATABASE nextcloud;
\q
exit
docker start nextcloud
```

#### Add missing indices
`docker exec --user www-data nextcloud php ./occ db:add-missing-indices`
### ToDo
- CrowdSec
- Authentik
- Complete this README.md
