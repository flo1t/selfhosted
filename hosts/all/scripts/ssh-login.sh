#!/bin/bash
. $(dirname "$0")/.env

# DISCORD_HIGHSECURITY_URL is set in the .env file
discord_url=$DISCORD_HIGHSECURITY_URL
discord_low_url=$DISCORD_LOWSECURITY_URL

if [ "${PAM_TYPE}" = "open_session" ]; then
  if [ "${PAM_RHOST}" = $RUNNER_IP ]; then # exclude runner ip from high alerts
    message="SSH login: ${PAM_USER} from ${PAM_RHOST}"
    json_payload="{\"content\":\"$message\",\"username\":\"$HOSTNAME\"}"
    curl -H "Content-Type: application/json" -d "$json_payload" "$discord_low_url"
  else
    message="SSH login: ${PAM_USER} from ${PAM_RHOST}"
    json_payload="{\"content\":\"$message\",\"username\":\"$HOSTNAME\"}"
    curl -H "Content-Type: application/json" -d "$json_payload" "$discord_url"
  fi
fi