import requests
from config import config
from datetime import datetime

def fetch_max_token_data():
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{config['max_token']}"
    response = requests.get(url)
    data = response.json().get("pair", {})

    return {
        "priceUsd": data.get("priceUsd"),
        "marketCap": data.get("marketCap"),
        "volume": data.get("volume", {}).get("h24"),
        "fdv": data.get("fdv"),
        "liquidity": data.get("liquidity", {}).get("usd"),
        "txns": data.get("txns", {}).get("h24", {}),
        "priceChange": data.get("priceChange", {}).get("h24"),
        "holders": "N/A",  # Not available via Dexscreener
        "timestamp": data.get("pairCreatedAt"),
        "url": data.get("url"),
    }

def is_allowed(user_id):
    return str(user_id) in config["whitelist"]

def format_number(value):
    return f"{value:,.2f}" if isinstance(value, (int, float)) else "N/A"

def format_launch_time(timestamp):
    if not timestamp:
        return "N/A"
    dt = datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime("%d %b %Y %I:%M %p")

def send_target_alerts():
    # Placeholder function for Tier 3 sell alerts (implement logic here)
    print("🚨 Simulating: Target price alerts triggered")
