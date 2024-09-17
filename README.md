# floit - selfhosted

## Description
This repository contains all docker-compose and configuration files for apps described on floit.ch.
Furthermore, the aim is to describe the installation and configuration of all apps.

## Overview

## ToDo
- Implement README.md for all services
- Remove setup-files when all services are documented

## Structure of this repository
| Folder | Purpose |
|---|---|
| .gitea/scripts | scripts for gitea actions |
| .gitea/workflows | gitea actions |
| hosts/all | subfolders will be published to all servers |
| hosts/hostname | subfolders will be published to *hostname* |
| templates | template files for docker compose, scripts, etc. |

## Host setup
| Folder | Purpose |
|---|---|
| ~/docker | docker compose data |
| ~/docker/*service* | folder for docker container *service* |
| ~/docker/*service*/.env | env file for docker container *service* |
| ~/docker/*service*/container-compose.yml | docker compose file for *service* |
| ~/docker/*service*/setup-files | non docker relevant files for *service* |
| ~/docker/*service*/data | *service* data (the name of the folder varies depending on the purpose) |
| ~/docker/*service*/logs | *service* logs (the name of the folder varies depending on the purpose) |
| ~/scripts | folder for scripts |

## Deployment
The docker repository is hosted on a Gitea repository, which rsyncs all changes within the repository to the according docker hosts.
