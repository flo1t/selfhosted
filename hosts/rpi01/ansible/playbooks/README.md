# floit - selfhosted

## Ansible

### Description
Ansible is an open-source automation engine used for IT automation tasks like configuration management, application deployment, and orchestration. It simplifies complex IT processes by using a declarative, human-readable language (YAML) to define automation tasks. Ansible is agentless, relying on SSH to communicate with managed nodes, making it easy to set up and use.
https://docs.ansible.com/

### Folderstructure
| Folder | Purpose |
|---|---|
| ~/ansible | folder for ansible configurations |
| ~/ansible/secret | ansible secret file |
| ~/ansible/playbooks | ansible playbooks |

### Setup

#### Add hosts
Update the variables in the hosts file file according to your setup:
```sh
sudo nano /etc/ansible/hosts

# add:
[servers]
rpi01 ansible_host=192.168.1.10
F-VSRV-01 ansible_host=192.168.1.15
```

#### Add variables
Upadte the variables in the hosts file according to your setup:
```sh
sudo nano /etc/ansible/hosts

# add:
[all:vars]
ansible_user='<user>'
ansible_become=yes
ansible_become_method=sudo
ansible_python_interpreter='auto_silent'
```

#### Add host ssh keys
Start the runner once to generate a config file:
`docker exec -ti gitea-runner /usr/local/bin/act_runner generate-config > /config/config.yaml`

Uncomment the "env_file: .env" line and change the network under container to "gitea_default":
`nano ~/docker/gitea/runner/config.yaml`


## Create SSH keys for cloning the repo
- Go to the client
- Open a terminal and run: `ssh-keygen -t ed25519 -C "<Computer- or Username>"` (no need for a password)
- Copy the public key `cat <path from above/id_ed25519.pub`
- Add the public key to the Gitea profile ssh keys (Profile -> Settings -> SSH / CPG Keys -> Add Key)
- Verify the public key (within the Gitea profile ssh keys) `echo -n '<Token> sh-keygen -Y sign -n gitea -f "<path from above>/id_ed25519.pub"`