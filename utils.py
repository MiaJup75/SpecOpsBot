import requests
from config import config
from datetime import datetime

def fetch_max_token_data():
    address = config["max_token"]
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json().get("pair")
    if not data:
        return None

    return {
        "price": data.get("priceUsd"),
        "market_cap": data.get("marketCap"),
        "fdv": data.get("fdv"),
        "volume": data.get("volume", {}).get("h24"),
        "txns": data.get("txns", {}).get("h24"),
        "liquidity": data.get("liquidity", {}).get("usd"),
        "price_change": data.get("priceChange", {}).get("h24"),
        "holders": data.get("holders", "N/A"),
        "launch_time": data.get("pairCreatedAt"),
        "link": data.get("url"),
    }

def fetch_trending_tokens():
    url = "https://api.dexscreener.com/latest/dex/search/?q=solana"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    pairs = response.json().get("pairs", [])
    trending = sorted(pairs, key=lambda x: x.get("volume", {}).get("h24", 0), reverse=True)[:5]

    result = []
    for token in trending:
        name = token.get("baseToken", {}).get("symbol", "N/A")
        price = token.get("priceUsd", "N/A")
        volume = token.get("volume", {}).get("h24", "N/A")
        result.append((name, price, volume))

    return result

def fetch_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    pairs = response.json().get("pairs", [])
    recent = [p for p in pairs if p.get("pairCreatedAt", 0) > 0]
    recent = sorted(recent, key=lambda x: x["pairCreatedAt"], reverse=True)[:5]

    return [(p["baseToken"]["symbol"], p["priceUsd"], p["url"]) for p in recent]

def check_suspicious_activity():
    # Placeholder logic for suspicious activity
    return []

def summarize_wallet_activity():
    return "No recent activity."

def get_pnl(address):
    return "$123 (up 17%)"  # Stub

def set_target_price(address, token, target):
    return f"✅ Target price of {target} set for {token}."

def check_target_price():
    return []

def suggest_gas_timing():
    return "Now is a low-MEV window for transactions."

def sentiment_score():
    return "🧠 Sentiment Score: 😈 Mischievous"
