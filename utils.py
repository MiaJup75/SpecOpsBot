import requests
import json

def is_allowed(user_id):
    try:
        with open("config.json") as f:
            config = json.load(f)
        return str(user_id) in config.get("whitelist", [])
    except:
        return False

def fetch_max_token_data():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        res = requests.get(url)
        data = res.json().get("pair", {})
        return {
            "price_usd": data.get("priceUsd"),
            "volume_usd": data.get("volume", {}).get("h24"),
            "liquidity_usd": data.get("liquidity", {}).get("usd"),
            "market_cap": data.get("fdv"),
            "price_change": data.get("priceChange", {}).get("h24"),
            "url": data.get("url")
        }
    except:
        return None

def get_trending_coins():
    # Placeholder mock data
    return [
        {"name": "SolDog", "price": "0.0012", "url": "https://dexscreener.com/solana/dummy1"},
        {"name": "SolMoon", "price": "0.0005", "url": "https://dexscreener.com/solana/dummy2"},
        {"name": "WAGMI", "price": "0.034", "url": "https://dexscreener.com/solana/dummy3"},
        {"name": "Frenz", "price": "0.0021", "url": "https://dexscreener.com/solana/dummy4"},
        {"name": "PepeSol", "price": "0.0007", "url": "https://dexscreener.com/solana/dummy5"},
    ]