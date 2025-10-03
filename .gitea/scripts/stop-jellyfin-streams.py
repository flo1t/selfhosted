import argparse
import sys
import requests
from requests.exceptions import RequestException

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--jellyfin_api_key", required=True)
    p.add_argument("--jellyfin_url", required=True)
    p.add_argument("--discord_url", required=True)
    p.add_argument("--excluded_users", default="")
    return p.parse_args()

def notify_discord(discord_session, discord_url, content, timeout):
    payload = {"content": content, "username": "JellyfinMonitor"}
    try:
        r = discord_session.post(discord_url, json=payload, timeout=timeout)
        r.raise_for_status()
        return True
    except RequestException:
        return False

def main():
    args = parse_args()

    API_KEY = args.jellyfin_api_key
    JELLYFIN_URL = args.jellyfin_url.rstrip("/")
    DISCORD_URL = args.discord_url
    EXCLUDED_USERS = [u.strip() for u in args.excluded_users.split(",") if u.strip()]

    TIMEOUT = 10

    # session for Jellyfin (includes Authorization)
    jf_session = requests.Session()
    jf_session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f'MediaBrowser Token="{API_KEY}"'
    })

    # separate session for Discord (no Authorization header)
    discord_session = requests.Session()
    discord_session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    })

    try:
        r = jf_session.get(f"{JELLYFIN_URL}/Sessions", timeout=TIMEOUT)
        r.raise_for_status()
        sessions = r.json()
    except RequestException as e:
        print(f"Failed to fetch sessions: {e}", file=sys.stderr)
        notify_discord(discord_session, DISCORD_URL, f"Jellyfin monitor: failed to fetch sessions: {e}", TIMEOUT)
        sys.exit(1)

    users_with_active_sessions = {}
    for s in sessions:
        username = s.get("UserName")
        now_playing = s.get("NowPlayingItem")
        playstate = s.get("PlayState", {})
        if not username or not now_playing:
            continue
        if playstate.get("IsPaused"):
            continue
        session_id = s.get("Id")
        last_checkin = s.get("LastPlaybackCheckIn")
        users_with_active_sessions.setdefault(username, []).append([session_id, last_checkin])

    if not users_with_active_sessions:
        print("No active sessions")
        return

    print(f"{len(users_with_active_sessions)} active sessions found. Checking simultaneous playbacks.")

    DATA_STOP = {"Text": "Too many simultaneous playbacks on this user: Stopping playback", "TimeoutMs": 30000}

    for user, sessions_list in users_with_active_sessions.items():
        count = len(sessions_list)
        if count <= 1:
            continue
        print(f"User {user} has {count} simultaneous streams.")
        # allow up to 3 for excluded users
        if user in EXCLUDED_USERS and count < 4:
            print(f"User {user} is excluded/allowed up to 3 streams.")
            continue

        for sess in sessions_list:
            session_id = sess[0]
            print(f"Killing session {session_id} and informing user {user}")

            # inform user (Message)
            try:
                msg_url = f"{JELLYFIN_URL}/Sessions/{session_id}/Message"
                r = jf_session.post(msg_url, json=DATA_STOP, timeout=TIMEOUT)
                r.raise_for_status()
            except RequestException as e:
                print(f"Couldn't inform user {user} about killing session {session_id}: {e}", file=sys.stderr)
                notify_discord(discord_session, DISCORD_URL, f"Simultaneous playbacks: Informing {user} about killing session {session_id} failed: {e}", TIMEOUT)

            # stop playback
            try:
                stop_url = f"{JELLYFIN_URL}/Sessions/{session_id}/Playing/Stop"
                r = jf_session.post(stop_url, timeout=TIMEOUT)
                r.raise_for_status()
                notify_discord(discord_session, DISCORD_URL, f"Simultaneous playbacks: Stopped session {session_id} from {user}", TIMEOUT)
            except RequestException as e:
                print(f"Couldn't stop session {session_id} for user {user}: {e}", file=sys.stderr)
                notify_discord(discord_session, DISCORD_URL, f"Simultaneous playbacks: Stopping session {session_id} from {user} failed: {e}", TIMEOUT)

if __name__ == "__main__":
    main()