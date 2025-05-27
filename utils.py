import requests
import json
import time
from datetime import datetime
from config import config

TELEGRAM_TOKEN = config["telegram_token"]
MAX_TOKEN_ADDRESS = config["max_token"]
DEXSCREENER_API = f"https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"

def fetch_max_token_data():
    try:
        response = requests.get(DEXSCREENER_API)
        data = response.json()
        pair = data["pair"]

        price = float(pair["priceUsd"])
        market_cap = float(pair.get("marketCap", 0))
        volume_24h = float(pair["volume"]["h24"])
        fdv = float(pair.get("fdv", 0))
        buys = pair["txns"]["h24"]["buys"]
        sells = pair["txns"]["h24"]["sells"]
        liquidity = float(pair["liquidity"]["usd"])
        change_24h = float(pair["priceChange"]["h24"])
        holders = "N/A"
        launch_timestamp = int(pair.get("pairCreatedAt", 0))
        if launch_timestamp:
            launch_time = datetime.utcfromtimestamp(launch_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            launch_time = "Unknown"

        return f"""
🐶 <b>MAX Token Update</b>
💰 Price: ${price:.8f}
🏛️ Market Cap: ${int(market_cap):,}
📉 Volume (24h): ${volume_24h:,.2f}
🏦 FDV: ${int(fdv):,}
📊 Buys: {buys} | Sells: {sells}
💧 Liquidity: ${liquidity:,.2f}
📈 24H Change: {change_24h:.2f}%
🔢 Holders: {holders}
🕐 Launch Time: {launch_time}
🔗 <a href="https://dexscreener.com/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc">View on Dexscreener</a>
        """.strip()
    except Exception as e:
        return f"⚠️ Error fetching MAX token data: {e}"

def is_allowed(user_id):
    return str(user_id) in config.get("whitelist", [])

def fetch_trending_tokens():
    # Placeholder for Tier 3+ trending engine
    return [
        {"symbol": "SOL", "price": 177.94, "volume": 104107},
        {"symbol": "MEME1", "price": 0.0002834, "volume": 1202},
        {"symbol": "MEME2", "price": 177.75, "volume": 1618010},
        {"symbol": "MEME3", "price": 177.61, "volume": 330633},
        {"symbol": "MEME4", "price": 177.83, "volume": 47040},
    ]

def get_trending_coins():
    coins = fetch_trending_tokens()
    message = "🚀 <b>Trending Solana Meme Coins</b>\n"
    for i, coin in enumerate(coins, 1):
        message += f"{i}. {coin['symbol']} – ${coin['price']} – Vol: ${int(coin['volume']):,}\n"
    return message

def summarize_wallet_activity():
    # Placeholder for wallet tracker summary
    return "📊 No major wallet activity in the last 24h."

def fetch_new_tokens():
    return "🆕 No new token launches in the last 12h."  # Placeholder for future Tier 4 smart scanning

def check_suspicious_activity():
    return "⚠️ No suspicious activity detected."  # Placeholder for future botnet/mirror alert
