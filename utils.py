import requests
import json
from config import config
from datetime import datetime

WHITELIST = [int(uid) for uid in config.get("whitelist", [])]

def is_allowed(user_id):
    return user_id in WHITELIST

def fetch_max_token_data():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        response = requests.get(url)
        data = response.json()["pair"]

        price = float(data["priceUsd"])
        market_cap = round(data.get("marketCap", 0))
        volume = round(data["volume"]["h24"], 2)
        fdv = round(data.get("fdv", 0))

        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${price:,.8f}
🏛️ Market Cap: ${market_cap:,}
📉 Volume (24h): ${volume:,}
🏦 FDV: ${fdv:,}"""

        return message

    except Exception as e:
        return f"⚠️ Error fetching MAX token data: {e}"

def get_trending_coins():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        response = requests.get(url)
        pairs = response.json()["pairs"][:5]

        message = "<b>🚀 Trending Solana Meme Coins</b>\n"
        for i, pair in enumerate(pairs, 1):
            name = pair["baseToken"]["name"]
            symbol = pair["baseToken"]["symbol"]
            price = pair["priceUsd"]
            vol = round(pair["volume"]["h24"], 2)
            message += f"{i}. {name} ({symbol}) – ${price} – Vol: ${vol:,}\n"

        return message
    except Exception as e:
        return f"⚠️ Error fetching trending coins: {e}"

def get_new_tokens():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        response = requests.get(url)
        pairs = response.json()["pairs"]

        new_tokens = []
        for pair in pairs:
            if not pair.get("pairCreatedAt"):
                continue
            age_ms = int(pair["pairCreatedAt"])
            age = datetime.fromtimestamp(age_ms / 1000)
            diff = datetime.utcnow() - age
            if diff.total_seconds() < 86400:  # 24 hours
                new_tokens.append(pair)

        if not new_tokens:
            return "⚠️ No new tokens launched in the last 24h."

        message = "<b>🆕 New Solana Tokens (Last 24h)</b>\n"
        for i, pair in enumerate(new_tokens[:5], 1):
            name = pair["baseToken"]["name"]
            symbol = pair["baseToken"]["symbol"]
            price = pair["priceUsd"]
            vol = round(pair["volume"]["h24"], 2)
            age = datetime.fromtimestamp(pair["pairCreatedAt"] / 1000).strftime("%H:%M %d %b")
            message += f"{i}. {name} ({symbol}) – ${price} – Vol: ${vol:,} – Created: {age}\n"

        return message

    except Exception as e:
        return f"⚠️ Error fetching new tokens: {e}"

def check_suspicious_activity():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        response = requests.get(url)
        pairs = response.json()["pairs"]

        flagged = []
        for pair in pairs:
            vol = pair["volume"]["h24"]
            buys = pair["txns"]["h1"]["buys"]
            sells = pair["txns"]["h1"]["sells"]
            if sells > buys * 2 and vol > 1000:
                flagged.append(pair)

        if not flagged:
            return "✅ No suspicious sell-offs detected."

        message = "<b>🚨 Suspicious Activity Detected</b>\n"
        for i, pair in enumerate(flagged[:5], 1):
            name = pair["baseToken"]["name"]
            symbol = pair["baseToken"]["symbol"]
            vol = round(pair["volume"]["h24"], 2)
            sells = pair["txns"]["h1"]["sells"]
            buys = pair["txns"]["h1"]["buys"]
            message += f"{i}. {name} ({symbol}) – Vol: ${vol:,} | Buys: {buys}, Sells: {sells}\n"

        return message

    except Exception as e:
        return f"⚠️ Error checking suspicious activity: {e}"

def get_wallet_activity():
    try:
        return "<b>👛 Wallet Monitoring</b>\nTracking wallet alerts coming soon in Tier 3..."
    except Exception as e:
        return f"⚠️ Error fetching wallet data: {e}"
