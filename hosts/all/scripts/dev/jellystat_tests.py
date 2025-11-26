import os
import urllib.request
from json import load, dumps
from dotenv import load_dotenv

load_dotenv()

JELLYSTAT_API_KEY = os.getenv('JELLYSTAT_API_KEY')

JELLYSTAT_URL = os.getenv('JELLYSTAT_URL')

#headers = {'Content-Type': 'application/json','Accept': 'application/json','User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 >
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
    'x-api-token': JELLYSTAT_API_KEY
}

req = urllib.request.Request(JELLYSTAT_URL + "/stats/getPlaybackActivity", headers=headers)

with urllib.request.urlopen(req) as response:
  sessions = load(response)

users_with_active_sessions = {}

for session in sessions:
  if "UserName" in session and "NowPlayingItem" in session:
    if not session["PlayState"]["IsPaused"]:
      user_session = [session["Id"], session["LastActivityDate"]]
      if session["UserName"] in users_with_active_sessions:
        users_with_active_sessions[session["UserName"]].append(user_session)
      else:
        users_with_active_sessions[session["UserName"]] = []
        users_with_active_sessions[session["UserName"]].append(user_session)

print(users_with_active_sessions)
