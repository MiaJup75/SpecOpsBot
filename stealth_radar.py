import requests
import datetime
from db import get_tokens

LAST_SCANNED = None

def fetch_new_tokens(since_minutes=30):
    global LAST_SCANNED
    now = datetime.datetime.utcnow()

    # Use a timestamp or filter logic to fetch tokens launched within last ~30 mins
    # For example, fetch from a token launch API, here is a placeholder:
    url = "https://public-api.solscan.io/launchpad/recent"  # Hypothetical endpoint
    try:
        resp = requests.get(url, timeout=10)
        tokens = resp.json()
        # Filter tokens launched after LAST_SCANNED time
        new_tokens = []
        for t in tokens:
            launch_time = datetime.datetime.fromisoformat(t['launchTime'])
            if not LAST_SCANNED or launch_time > LAST_SCANNED:
                new_tokens.append(t)
        LAST_SCANNED = now
        return new_tokens
    except Exception as e:
        print(f"[StealthRadar] API fetch error: {e}")
        return []

def filter_suspicious(tokens):
    suspicious = []
    for token in tokens:
        # Example suspicious criteria
        if token['liquidity'] < 10000:
            suspicious.append(token)
        elif token['socialSignals'] < 5:
            suspicious.append(token)
    return suspicious
