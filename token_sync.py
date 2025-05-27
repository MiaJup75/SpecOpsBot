import requests
from db import add_token

def fetch_trending_tokens():
    url = "https://api.dexscreener.com/latest/dex/trending/solana"
    try:
        res = requests.get(url, timeout=10).json()
        tokens = [t['token']['symbol'] for t in res.get('pairs', []) if 'token' in t]
        return tokens
    except Exception as e:
        print(f"[TokenSync] Error fetching trending tokens: {e}")
        return []

def sync_trending_tokens():
    tokens = fetch_trending_tokens()
    for t in tokens:
        add_token(t)
