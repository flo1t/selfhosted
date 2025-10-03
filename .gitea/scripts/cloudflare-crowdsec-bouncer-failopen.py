#!/usr/bin/env python3
import os
import sys
import argparse
import requests

parser = argparse.ArgumentParser(description="Enable request_limit_fail_open for Cloudflare Worker routes (multiple routes supported)")
parser.add_argument('--zone', '-z', help='Cloudflare Zone ID')
parser.add_argument('--route_patterns', '-p', action='append',
                    help='Route pattern(s). Provide multiple -p entries or comma-separated values. Example: -p "*example.com/*" -p "*abc.de/*"')
parser.add_argument('--route_worker', '-w', help='Worker name (default: crowdsec-cloudflare-worker-bouncer)',
                    default='crowdsec-cloudflare-worker-bouncer')
parser.add_argument('--token', '-t', help='Cloudflare API token')
parser.add_argument('--discord', '-d', help='Discord webhook URL to notify on failures')
args = parser.parse_args()

ZONE = args.zone
PATTERNS_RAW = args.route_patterns
WORKER = args.route_worker
TOKEN = args.token
DISCORD_URL = args.discord

# Discord headers as requested
DISCORD_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
}

def notify_discord(message: str):
    if not DISCORD_URL:
        return
    try:
        requests.post(DISCORD_URL, json={'content': message}, headers=DISCORD_HEADERS, timeout=5)
    except Exception as e:
        print("Failed to send Discord notification:", e, file=sys.stderr)

if not ZONE:
    msg = "Missing CLOUDFLARE_ZONE_ID"
    print(msg, file=sys.stderr)
    notify_discord(f"[Cloudflare script] ERROR: {msg}")
    sys.exit(2)
if not PATTERNS_RAW:
    msg = "Missing CLOUDFLARE_ROUTE_PATTERNS"
    print(msg, file=sys.stderr)
    notify_discord(f"[Cloudflare script] ERROR: {msg}")
    sys.exit(3)
if not TOKEN:
    msg = "Missing CLOUDFLARE_API_TOKEN"
    print(msg, file=sys.stderr)
    notify_discord(f"[Cloudflare script] ERROR: {msg}")
    sys.exit(4)

# Build list of patterns (simple split)
patterns = []
if isinstance(PATTERNS_RAW, list):
    for item in PATTERNS_RAW:
        for p in str(item).split(','):
            p = p.strip()
            if p:
                patterns.append(p)
else:
    for p in str(PATTERNS_RAW).split(','):
        p = p.strip()
        if p:
            patterns.append(p)

# dedupe, preserve order
seen = set()
patterns = [p for p in patterns if not (p in seen or seen.add(p))]
if not patterns:
    msg = "No valid patterns after parsing."
    print(msg, file=sys.stderr)
    notify_discord(f"[Cloudflare script] ERROR: {msg} (input: {PATTERNS_RAW})")
    sys.exit(3)

CF_HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
url = f'https://api.cloudflare.com/client/v4/zones/{ZONE}/workers/routes'

try:
    resp = requests.get(url, headers=CF_HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    msg = f"Failed to fetch routes: {e}"
    print(msg, file=sys.stderr)
    notify_discord(f"[Cloudflare script] ERROR: {msg}")
    sys.exit(5)

routes = data.get('result', [])
if not isinstance(routes, list):
    msg = 'Unexpected API response: "result" not a list'
    print(msg, file=sys.stderr)
    notify_discord(f"[Cloudflare script] ERROR: {msg} (response: {data})")
    sys.exit(6)

updated = skipped = errors = 0

for r in routes:
    route_pattern = r.get('pattern') or ''
    route_script = r.get('script') or ''
    route_id = r.get('id')
    if route_pattern not in patterns:
        continue
    if WORKER and WORKER != route_script:
        continue

    if r.get('request_limit_fail_open'):
        print(f"[SKIP] {route_id} {route_pattern} already enabled")
        skipped += 1
        continue

    payload = {'pattern': route_pattern, 'script': route_script, 'request_limit_fail_open': True}
    put_url = f'{url}/{route_id}'
    try:
        put_resp = requests.put(put_url, headers=CF_HEADERS, json=payload, timeout=10)
        put_resp.raise_for_status()
        put_json = put_resp.json()
        if put_json.get('success'):
            print(f"[OK] updated {route_id} {route_pattern}")
            updated += 1
        else:
            print(f"[ERR] API returned success=false for {route_id}: {put_json}", file=sys.stderr)
            errors += 1
    except Exception as e:
        print(f"[ERR] updating {route_id}: {e}", file=sys.stderr)
        errors += 1

summary = f"patterns={patterns}, updated={updated}, skipped={skipped}, errors={errors}"
print("Summary:", summary)
if errors:
    notify_discord(f"[Cloudflare script] FAILED: {summary}")
sys.exit(1 if errors else 0)