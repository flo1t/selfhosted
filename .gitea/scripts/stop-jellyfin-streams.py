import os
import urllib.request
import argparse, sys
from json import load, dumps
import datetime

parser=argparse.ArgumentParser()
parser.add_argument("--jellyfin_api_key")
parser.add_argument("--jellyfin_url")
parser.add_argument("--discord_url")
parser.add_argument("--excluded_users")
args=parser.parse_args()

API_KEY = args.jellyfin_api_key
JELLYFIN_URL = args.jellyfin_url
DISCORD_JELLYFIN_URL=args.discord_url
EXCLUDED_USERS=args.excluded_users.split(",")

# User-Agent needed for discord, otherwise the request gets blocked
headers = {'Content-Type': 'application/json','Accept': 'application/json','User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
# TimeoutMs has no effect
data_stop = {'Text':'Too many simultaneous playbacks on this user: Stopping playback','TimeoutMs':'30000'}

with urllib.request.urlopen(JELLYFIN_URL + "/Sessions" + "?api_key=" + API_KEY) as response:
  sessions = load(response)

users_with_active_sessions = {}

for session in sessions:
  if "UserName" in session and "NowPlayingItem" in session:
    if not session["PlayState"]["IsPaused"]:
      user_session = [session["Id"], session["LastPlaybackCheckIn"]]
      if session["UserName"] in users_with_active_sessions:
        users_with_active_sessions[session["UserName"]].append(user_session)
      else:
        users_with_active_sessions[session["UserName"]] = []
        users_with_active_sessions[session["UserName"]].append(user_session)

if len(users_with_active_sessions) >= 1:
  print(f"{len(users_with_active_sessions)} active sessions found. Checking if they have simultaneous playbacks.")
else:
  print(f"No active sessions")

for user in users_with_active_sessions:
  if len(users_with_active_sessions[user]) > 1:
    print(f"User {user} has {len(users_with_active_sessions[user])} simultaneuos streams.")
    if user in EXCLUDED_USERS:
      print(f"But it's {user} and therefore allowed to have simultaneous streams.")
    else:
      for session in users_with_active_sessions[user]:
        id = session[0]
        print(f"Killing session {id} and informing user")
        try:
          req = urllib.request.urlopen(urllib.request.Request(JELLYFIN_URL + "/Sessions/" + id  + "/Message?api_key=" + API_KEY, dumps(data_stop).encode("utf-8"), headers))
        except:
          print(f"Couldn't inform user {user} about killing session {id}")
          discord_message = {'content':f'Simultaneous playbacks: Informing ${user} about killing session {id} failed','username':'Gitea Action'}
          req = urllib.request.urlopen(urllib.request.Request(DISCORD_JELLYFIN_URL, dumps(discord_message).encode("utf-8"), headers))
        try:
          req = urllib.request.urlopen(urllib.request.Request(JELLYFIN_URL + "/Sessions/" + id  + "/Playing/Stop?api_key=" + API_KEY, method="POST"))
          discord_message = {'content':f'Simultaneous playbacks: Stopped session {id} from {user}','username':'Gitea Action'}
          req = urllib.request.urlopen(urllib.request.Request(DISCORD_JELLYFIN_URL, dumps(discord_message).encode("utf-8"), headers))
        except:
          print(f"Couldn't kill session {id} for user {user}")
          discord_message = {'content':f'Simultaneous playbacks: Stopping session {id} from {user} failed','username':'Gitea Action'}
          req = urllib.request.urlopen(urllib.request.Request(DISCORD_JELLYFIN_URL, dumps(discord_message).encode("utf-8"), headers))