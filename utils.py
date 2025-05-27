import requests
import json
from datetime import datetime, timezone
from config import config

MAX_TOKEN = config['max_token']
DEXSCREENER_API = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"

def fetch_max_token_data():
    try:
        response = requests.get(DEXSCREENER_API)
        data = response.json().get('pair', {})
        if not data:
            return None

        return {
            'price': data.get('priceUsd'),
            'market_cap': data.get('marketCap'),
            'volume': data.get('volume', {}).get('h24'),
            'fdv': data.get('fdv'),
            'txns': data.get('txns', {}).get('h24', {}),
            'holders': None,  # Not available on Dexscreener
            'liquidity': data.get('liquidity', {}).get('usd'),
            'price_change': data.get('priceChange', {}).get('h24'),
            'launch_age': datetime.now(timezone.utc).timestamp() - int(data.get('pairCreatedAt', 0)) / 1000,
            'dex_url': data.get('url')
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch MAX token data: {e}")
        return None

def get_trending_coins():
    try:
        response = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
        data = response.json().get("pairs", [])
        sorted_data = sorted(data, key=lambda x: float(x.get("volume", {}).get("h24", 0)), reverse=True)
        return sorted_data[:5]
    except Exception as e:
        print(f"[ERROR] Failed to fetch trending coins: {e}")
        return []

def get_new_tokens():
    try:
        response = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
        tokens = response.json().get("pairs", [])
        new_tokens = [t for t in tokens if t.get("pairCreatedAt", 0) >= (datetime.now(timezone.utc).timestamp() - 43200) * 1000]
        return new_tokens[:5]
    except Exception as e:
        print(f"[ERROR] Failed to fetch new tokens: {e}")
        return []

def check_suspicious_activity():
    try:
        response = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
        data = response.json().get("pairs", [])
        flagged = []
        for pair in data:
            if pair.get("volume", {}).get("h24", 0) > 10000 and abs(pair.get("priceChange", {}).get("h24", 0)) > 30:
                flagged.append(pair)
        return flagged[:5]
    except Exception as e:
        print(f"[ERROR] Failed to detect suspicious activity: {e}")
        return []

def is_allowed(user_id):
    return str(user_id) in config.get("whitelist", [])