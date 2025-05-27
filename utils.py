import requests
from config import config

def fetch_max_token_data():
    address = config["max_token"]
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    try:
        response = requests.get(url)
        data = response.json().get("pair", {})
        return {
            "price": data.get("priceUsd"),
            "market_cap": data.get("marketCap"),
            "volume": data.get("volume", {}).get("h24"),
            "fdv": data.get("fdv")
        }
    except Exception as e:
        return None

def is_allowed(user_id):
    return str(user_id) in config.get("whitelist", [])

def get_trending_coins():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url)
        pairs = response.json().get("pairs", [])
        sorted_pairs = sorted(
            [p for p in pairs if p.get("baseToken", {}).get("symbol") != "SOL"],
            key=lambda x: x.get("volume", {}).get("h24", 0),
            reverse=True
        )[:5]
        return sorted_pairs
    except Exception:
        return []

def fetch_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url)
        pairs = response.json().get("pairs", [])
        new_tokens = []
        for token in pairs:
            if token.get("pairCreatedAt"):
                new_tokens.append(token)
        return sorted(new_tokens, key=lambda x: x["pairCreatedAt"], reverse=True)[:5]
    except Exception:
        return []

def check_suspicious_activity():
    return [
        {"token": "RUGDOG", "flag": "🚨 Liquidity pulled"},
        {"token": "FAKEAI", "flag": "⚠️ Dev wallet dumped 80%"},
    ]

def track_position(held_tokens=10_450_000, buy_price=0.0002):
    current = fetch_max_token_data()
    if not current:
        return None
    current_price = float(current["price"])
    value = held_tokens * current_price
    invested = held_tokens * buy_price
    pnl = value - invested
    return {
        "value": round(value, 2),
        "pnl": round(pnl, 2),
        "breakeven": round(buy_price, 6)
    }

def get_token_info(address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
    try:
        res = requests.get(url)
        token_data = res.json().get("pairs", [])[0]
        return {
            "symbol": token_data["baseToken"]["symbol"],
            "price": token_data["priceUsd"],
            "volume": token_data["volume"]["h24"],
            "liquidity": token_data["liquidity"]["usd"],
        }
    except Exception:
        return None

def summarize_wallet_activity(wallet_address):
    # Dummy placeholder for now
    return f"Wallet {wallet_address[:4]}...{wallet_address[-4:]} activity summary:\n🟢 2 Buys, 🔴 1 Sell in last 24h"
