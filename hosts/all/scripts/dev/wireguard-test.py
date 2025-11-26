import os
import requests
from json import load
from dotenv import load_dotenv

load_dotenv()

WIREGUARD_URL = os.getenv('WIREGUARD_URL')
WIREGUARD_PASSWORD = os.getenv('WIREGUARD_PW')

def get_session_id():
    """Authenticate and get session cookie"""
    auth_url = f"{WIREGUARD_URL}/api/session"
    headers = {'Content-Type': 'application/json'}
    data = {"password": WIREGUARD_PASSWORD}
    try:
        response = requests.post(auth_url, headers=headers, json=data)
        response.raise_for_status()
        return response.cookies.get('connect.sid')
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {e}")
        return None

def get_metrics(session_id):
    """Get client data using authenticated session"""
    clients_url = f"{WIREGUARD_URL}/api/wireguard/client"
    headers = {
        'Cookie': f'connect.sid={session_id}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(clients_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    session_id = get_session_id()
    if session_id:
        metrics = get_metrics(session_id)
        if metrics:
            print("WireGuard Clients:")
            for client in metrics:
                print(f"ID: {client['id']}, Name: {client['name']}, LatestHandshake: {client['latestHandshakeAt']}")
        else:
            print("No client data received")