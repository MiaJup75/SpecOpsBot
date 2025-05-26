
import requests
import json

with open("config.json", "r") as f:
    config = json.load(f)

MAX_TOKEN = config["max_token"]
WALLETS = config["wallets"]
WHITELIST = config["whitelist"]
DEXSCREENER_API = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"

def fetch_max_token_data():
    try:
        response = requests.get(DEXSCREENER_API)
        if response.status_code != 200:
            return None
        data = response.json().get("pair")
        return {
            "priceUsd": data["priceUsd"],
            "volume": data["volume"]["h24"],
            "liquidity": data["liquidity"]["usd"],
            "fdv": data["fdv"],
            "marketCap": data["marketCap"],
            "buys": data["txns"]["h24"]["buys"],
            "sells": data["txns"]["h24"]["sells"]
        }
    except Exception:
        return None

def fetch_trending_coins():
    # Placeholder dummy data
    return [
        "1. PEPE  🚀",
        "2. BONK  🐶",
        "3. WEN   💧",
        "4. SAMO  🐕",
        "5. TOSHI 🧠"
    ]

def is_allowed(user_id):
    return str(user_id) in WHITELIST
