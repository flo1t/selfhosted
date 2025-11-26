# floit - selfhosted

## Authentik

### Description
Authentik is an open-source Identity Provider.
https://goauthentik.io/

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/authentik | folder for authentik |
| ~/docker/authentik/.env | env file for secrets |
| ~/docker/authentik/authentik-compose.yml | docker compose file |
| ~/docker/authentik/setup-files | folder for custom files, which are not used from docker |
| ~/docker/authentik/media | media folder |
| ~/docker/authentik/templates | template folder |
| ~/docker/authentik/certs | cert data |
| ~/docker/authentik/certbot | certbot folder |
| ~/docker/authentik/db | db folder |

### Setup
#### Overview
I'm using Authentik to protect services from unwanted access and as SSO-provider. Certbot will take care of the certificate for LDAP.

#### Prerequisites
- Traefik
- Cloudflare API key (Permissions: Zone.DNS - Edit)

#### Setup Docker container
Prepare the folder structure:
```sh
mkdir -p ~/docker/authentik/{db,media,templates,certs,certbot}
touch ~/docker/authentik/.env
sudo chmod 600 ~/docker/authentik/.env
```

Prepare the .env file:
```sh
sudo apt install -y pwgen
echo "PG_USER=$(pwgen -s 10 1)" >> ~/docker/authentik/.env
echo "PG_PASS=$(pwgen -s 40 1)" >> ~/docker/authentik/.env
echo "AUTHENTIK_SECRET_KEY=$(pwgen -s 50 1)" >> ~/docker/authentik/.env
echo "AUTHENTIK_ERROR_REPORTING__ENABLED=true" >> ~/docker/authentik/.env
```

Update all variables in the .env file according to your setup. Some of the variables are generated in a later step.
```sh
nano ~/docker/authentik/.env

# add:
AUTHENTIK_EMAIL__HOST=<mail host>
AUTHENTIK_EMAIL__PORT=<mail port>
AUTHENTIK_EMAIL__USERNAME=<mail username>
AUTHENTIK_EMAIL__PASSWORD=<mail pw>
AUTHENTIK_EMAIL__USE_TLS=false
AUTHENTIK_EMAIL__USE_SSL=true
AUTHENTIK_EMAIL__TIMEOUT=10
AUTHENTIK_EMAIL__FROM=<mail address>

DOMAIN=<domain>
HOST=<authentik host>
```

Create the cloudflare.ini file for generating the LDAP cert `nano ~/docker/authentik/cloudflare.ini`:
```
# Cloudflare API token used by Certbot
dns_cloudflare_api_token = token
```

Start the Docker container:
`docker compose -f ~docker/authentik/authentik-compose.yml up -d`

Add a dns entry for Authentik.

#### Traefik basic setup
Using forward auth uses your existing reverse proxy to do the proxying, and only uses the authentik outpost to check authentication and authorization.

Add a middleware for this (traefik/data/rules/middlewares.yml / traefik/data/rules/middlewares-chains.yml):
```yml
    authentik:
      forwardauth:
        address: http://authentik-server:9000/outpost.goauthentik.io/auth/traefik
        trustForwardHeader: true
        authResponseHeaders:
          - X-authentik-username
          - X-authentik-groups
          - X-authentik-email
          - X-authentik-name
          - X-authentik-uid
          - X-authentik-jwt
          - X-authentik-meta-jwks
          - X-authentik-meta-outpost
          - X-authentik-meta-provider
          - X-authentik-meta-app
          - X-authentik-meta-version
```

### Add services
Consult the Authentik documentation for service implementation. The documentation is quite comprehensive. I'll add some special services below.
https://docs.goauthentik.io/integrations/services/

#### Traefik Dashboard
Open the authentik settings and:
- Add Provider:
	- Name: Traefik Dashboard ForwardAuth
	- Authorization: default-provider-authorization-implicit-consent (Authorize Application)
	- Forward Auth (single application):
		- External URL: https://<traefik fqdn>
- Add Application:
	- Name: Traefik Dashboard
	- Slug: traefik
	- Provider: Traefik Dashboard ForwardAuth
- Change Outposts:
	- Integration: Local Docker connection
	- Applications: Add Traefik Dashboard
	- Advanced Settings: docker_network: proxy

### *Arr services and SabNZBD
Repeat for each *arr service:
- Add Provider:
	- Name: Sonarr ForwardAuth
	- Authorization: default-provider-authorization-implicit-consent (Authorize Application)
	- Forward Auth (single application):
		- External URL: https://<sonarr fqdn>
	- Enable "Send HTTP-Basic Authentication"
		- arr_user
		- arr_password
- Add application:
	- Name: Sonarr
	- Slug: Sonarr
	- Provider: Sonarr ForwardAuth
- Change Outposts:
	- Applications: Add Sonarr
- Create Group:
	- Add custom attributes:
```
arr_user = admin
arr_password = <pw>
```
SabNZDB:
- Go to Settings -> Special
    - Uncheck html_form

Add middleware to each service `nano ~/docker/traefik/data/rules/app-download.yml`: chain-basic-auth

#### LDAP
Informations to use the LDAP provider:
- Server address: <authentik fqdn>
- BaseDN: DC=ldap,DC=<domain>,DC=<top level domain>
- User: ldapservice
- PW: <pw>

### ToDo
- Check if there is a different solution for certbot (triggers an monitoring alert, as the container just starts up and stops then)
- Implement some kind of monitoring