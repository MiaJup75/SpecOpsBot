
import json
import requests
from datetime import datetime

with open("config.json") as f:
    config = json.load(f)

def is_allowed(update):
    user_id = str(update.effective_user.id)
    return user_id in config["whitelist"]

def fetch_max_token_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    try:
        response = requests.get(url)
        data = response.json()["pair"]
        price = data["priceUsd"]
        market_cap = data["marketCap"]
        volume = data["volume"]["h24"]
        fdv = data["fdv"]
        txns = data["txns"]["h24"]
        holders = "N/A"
        liquidity = data["liquidity"]["usd"]
        price_change = data["priceChange"]["h24"]
        launch_age = datetime.utcfromtimestamp(data["pairCreatedAt"] / 1000).strftime("%Y-%m-%d %H:%M:%S")

        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${price}
🏛️ Market Cap: ${market_cap}
📉 Volume (24h): ${volume}
🏦 FDV: ${fdv}
🔁 24H TXNs: Buys {txns['buys']} / Sells {txns['sells']}
👥 Holders: {holders}
💧 Liquidity: ${liquidity}
📈 24H Change: {price_change}%
⏱️ Launch Time: {launch_age}
"""
        return message
    except Exception as e:
        return f"❌ Error fetching MAX token data: {e}"

def get_trending_coins():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url)
        data = response.json().get("pairs", [])[:5]
        message = "🚀 <b>Trending Solana Meme Coins</b>
"
        for i, coin in enumerate(data, 1):
            symbol = coin["baseToken"]["symbol"]
            price = coin["priceUsd"]
            vol = coin["volume"]["h24"]
            message += f"{i}. {symbol} – ${price} – Vol: ${vol}
"
        return message
    except Exception as e:
        return f"❌ Error fetching trending coins: {e}"

def check_suspicious_activity():
    # Stub logic for suspicious activity detection
    return "⚠️ No suspicious activity detected in the past 24 hours."

def analyze_new_tokens():
    # Stub logic for new token detection
    return "🆕 No new tokens launched in the past 12 hours."

