import requests
from config import config

def fetch_max_token_data():
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        response = requests.get(url)
        data = response.json()["pair"]

        return {
            "price": float(data["priceUsd"]),
            "market_cap": int(data["marketCap"]),
            "volume": float(data["volume"]["h24"]),
            "fdv": int(data["fdv"]),
            "buys": data["txns"]["h24"]["buys"],
            "sells": data["txns"]["h24"]["sells"],
            "liquidity_usd": float(data["liquidity"]["usd"]),
            "change_24h": float(data["priceChange"]["h24"]),
            "holders": "N/A",  # Placeholder
            "launch_time": data.get("pairCreatedAt"),
            "url": data["url"]
        }
    except Exception as e:
        print(f"[ERROR] fetch_max_token_data: {e}")
        return None

def get_trending_coins():
    # Simulated top 5 trending coins
    return [
        {"name": "DOGGO", "price": 0.0009, "volume": 12345},
        {"name": "MEOW", "price": 0.0012, "volume": 8901},
        {"name": "ZAP", "price": 0.045, "volume": 22000},
        {"name": "RAWR", "price": 0.00005, "volume": 3210},
        {"name": "BLOOP", "price": 0.75, "volume": 18450}
    ]

def get_new_token_launches():
    # Simulated new token launch data
    return []

def check_suspicious_activity():
    # Simulated suspicious activity check
    return []

def track_wallet_activity():
    # Simulated wallet tracking activity
    return []

def track_position():
    # Placeholder logic for PnL
    return "📈 PnL Tracker:\nBreak-even: $0.00032\nCurrent: $0.00034\nPnL: +6.25%"

def is_allowed(user_id):
    return str(user_id) in config["whitelist"]
