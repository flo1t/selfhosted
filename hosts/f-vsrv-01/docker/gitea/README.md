# floit - selfhosted

## gitea

### Description
Gitea is a DevOps platform similar to GitHub. It enables the creation and management of repositories based on Git and features an integrated CI/CD system, Gitea Actions, that is compatible with GitHub Actions. 
https://about.gitea.com/

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/docker/gitea | folder for gitea |
| ~/docker/gitea/.env | env file for secrets |
| ~/docker/gitea/gitea-compose.yml | docker compose file |
| ~/docker/gitea/setup files | folder for custom files, which are not used from docker |
| ~/docker/gitea/data | data folder |
| ~/docker/gitea/runner | folder for the runners |
| ~/docker/gitea/db | database folder |

### Setup

#### Setup Docker container
Prepare the folder structure:
`mkdir -p mkdir -p ~/docker/gitea/{data,db,runner}`

Update the variables in the .env file according to your setup:
```sh
nano ~/docker/gitea/.env

# add:
GITEA_DB=<db name>
GITEA_USER=<db user>
GITEA_USER_PW=<db user pw>
LOCAL_ROOT_URL=<gitea fqdn>
SELFHOSTED_RUNNER_TOKEN=<gitea runner token>
SELFHOSTED_RUNNER_NAME=<gitea runner name>
```

Start the Docker container:
`docker compose -f ~docker/gitea/gitea-compose.yml up -d`

#### Traefik
My Traefik container is running on a different host. Because of that I can't use Docker labels and have to create a rule file (setup-files\app-gitea.yml) under ~/docker/traefik/data/rules/app-gitea.yml on the host running Traefik.

Don't forget to add DNS entries for reaching the service.

#### Setup the runner
Start the runner once to generate a config file:
`docker exec -ti gitea-runner /usr/local/bin/act_runner generate-config > /config/config.yaml`

Uncomment the "env_file: .env" line and change the network under container to "gitea_default":
`nano ~/docker/gitea/runner/config.yaml`

#### Authentik
I'm using Authentik as identity provider. To implement it, follow the official Authentik guide: https://docs.goauthentik.io/integrations/services/gitea.

### Actions
#### Automatic deployment of the git repository
I'm deploying the docker and script files automatically via Gitea Action to the hosts (on file changes inside the hosts folder). For that, the Gitea runner authenticates via SSH to the hosts. Therefore I've added a public key from each host as Gitea Secret, which is accesible via Gitea Action.
- Logon to each host an execute: `ssh-keygen -t ed25519 -C "Gitea runner" -f ~/.ssh/id_ed25519_gitea_runner` (no need for a password)
- Copy the public key to the authorized_keys: `cat ~/.ssh/id_ed25519_gitea_runner.pub >> ~/.ssh/authorized_keys`
- Copy the private key `cat ~/.ssh/id_ed25519_gitea_runner`
- Add the private key to the Gitea repository secrets (Repository -> Settings -> Actions -> Secrets)
    - Follow this naming scheme: SSH_*HOST*_PRIVATE_KEY (replace *HOST* with your hostname)
- Add the Gitea repository variables "LOCAL_DOMAIN" (for the host fqdn) and "HOMEDIR" (for the docker and scripts data folder) (Repository -> Settings -> Actions -> Variables)
- Update the deploy-changes-to-hosts.yml file (.gitea\workflows\) according to your setup
    - Replace the hosts in the `declare -A HOSTS..` ` with your hostnames and your secret names (from above)

## Create SSH keys for cloning the repo
- Go to the client
- Open a terminal and run: `ssh-keygen -t ed25519 -C "<Computer- or Username>"` (no need for a password)
- Copy the public key `cat <path from above/id_ed25519.pub`
- Add the public key to the Gitea profile ssh keys (Profile -> Settings -> SSH / CPG Keys -> Add Key)
- Verify the public key (within the Gitea profile ssh keys) `echo -n '<Token> sh-keygen -Y sign -n gitea -f "<path from above>/id_ed25519.pub"`