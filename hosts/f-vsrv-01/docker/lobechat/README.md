# floit - selfhosted

## lobechat

### Description
An open-source, modern-design ChatGPT/LLMs UI/Framework.
https://github.com/lobehub/lobe-chat

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/lobechat | folder for lobechat |
| ~/docker/lobechat/.env | env file for secrets |
| ~/docker/lobechat/lobechat-compose.yml | docker compose file |
| ~/docker/lobechat/data | data folder |
| ~/docker/lobechat/db | database folder |

### Setup

#### Setup Docker container
Prepare the folder structure:
`mkdir -p ~/docker/lobechat/{data,db,searxng}`

Update the variables in the .env file according to your setup:
```sh
nano ~/docker/lobechat/.env

# add:
# general settings
TZ=Europe/Zurich

# lobechat settings
APP_URL=https://<LOBECHAT_FQDN>
KEY_VAULTS_SECRET='<random-key>'
LOBECHAT_FQDN=<LOBECHAT_FQDN>

# gpt api keys
DEEPSEEK_API_KEY='<api-key>'
OPENAI_API_KEY='<api-key>'
PERPLEXITY_API_KEY='<api-key>'

# postgres
LOBE_DB=<lobe-db>
LOBE_DB_USER=<lobe-db-user>
LOBE_DB_PASSWORD='<lobe-db-password>'

# minio
MINIO_FQDN=<MINIO_FQDN>
MINIO_DASHBOARD_FQDN=<MINIO_DASHBOARD_FQDN>
MINIO_ROOT_USER=<minio-user>
MINIO_ROOT_PASSWORD='<minio-password>'
S3_BUCKET=<bucket-name>
S3_ACCESS_KEY_ID=<minio-access-key>
S3_SECRET_ACCESS_KEY=<minio-secret-access-key>
S3_PUBLIC_DOMAIN=https://<MINIO_FQDN>
S3_LOCAL_DOMAIN=https://<MINIO_DASHBOARD_FQDN>

# authentik
NEXT_AUTH_SECRET='<random-key>'
AUTH_AUTHENTIK_ID='<authentik-od>'
AUTH_AUTHENTIK_SECRET='<authentik-secret>'
AUTH_AUTHENTIK_ISSUER=<authentik-issuer>
NEXTAUTH_URL=https://<LOBECHAT_FQDN>/api/auth
```

Start the Docker container:
`docker compose -f ~docker/lobechat/lobechat-compose.yml up -d`

#### Setup SearXNG
Include json format in the settings.yml
`sudo nano ~/docker/lobechat/searxng/settings.yml`

#### DNS
Don't forget to add DNS entries for reaching the service.

#### Setup the Minio bucket
Navigate to "http://192.168.1.10:9090/browser"
- Create the bucket "lobe"
- Add a access policy on the bucket (see setup-files/minio-access-policy.json)
- Go to access key and create a token
- Add the token to the .env file

#### Authentik
I'm using Authentik as identity provider. To implement it, follow the official Lobechat Authentik guide: https://lobehub.com/docs/self-hosting/advanced/auth/next-auth/authentik .