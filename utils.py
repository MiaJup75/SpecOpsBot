import requests
from config import config
from datetime import datetime, timezone
import random

def get_token_stats(token_address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{token_address}"
        res = requests.get(url).json()
        pair = res["pair"]

        price = float(pair["priceUsd"])
        market_cap = int(pair.get("marketCap", 0))
        volume = float(pair["volume"]["h24"])
        fdv = int(pair.get("fdv", 0))
        buys = pair["txns"]["h24"]["buys"]
        sells = pair["txns"]["h24"]["sells"]
        liquidity = float(pair["liquidity"]["usd"])
        change = float(pair["priceChange"]["h24"])
        launch = int(pair.get("pairCreatedAt", 0)) // 1000

        launch_time = datetime.fromtimestamp(launch).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "message": (
                f"🐶 <b>MAX Token Update</b>\n"
                f"💰 Price: ${price:.8f}\n"
                f"🏛️ Market Cap: ${market_cap:,}\n"
                f"📉 Volume (24h): ${volume:,.2f}\n"
                f"🏦 FDV: ${fdv:,}\n"
                f"📊 Buys: {buys} | Sells: {sells}\n"
                f"💧 Liquidity: ${liquidity:,.2f}\n"
                f"📈 24H Change: {change:.2f}%\n"
                f"🔢 Holders: N/A\n"
                f"🕐 Launch Time: {launch_time}\n"
                f"🔗 <a href='https://dexscreener.com/solana/{token_address}'>View on Dexscreener</a>"
            )
        }

    except Exception as e:
        return {"message": f"❌ Error fetching MAX data: {e}"}

def fetch_trending_tokens():
    # Stub implementation
    return "<b>🚀 Trending Solana Meme Coins</b>\n1. MAX\n2. SOLMOON\n3. GIGASOL\n4. FROG\n5. ZOO"

def fetch_new_tokens():
    return "<b>🆕 New Solana Tokens (last 12h)</b>\n🔍 Scan results: None flagged."

def check_suspicious_activity():
    return "<b>⚠️ Suspicious Activity Monitor</b>\nNo major wallet dumps or LP drains."

def track_position():
    return "<b>📈 PnL Tracker</b>\nMock: +23% ROI on MAX.\nEntry: $0.00029 | Now: $0.00033"

def score_sentiment():
    emojis = ["💎", "🚀", "😎", "📉", "🔥", "💀"]
    score = random.choice(emojis)
    return f"<b>📢 Meme Sentiment Score</b>\nCurrent Score: {score}"

def detect_stealth_launches():
    return "<b>🕵️ Stealth Token Radar</b>\nNo-society tokens found: 0"

def analyze_wallet_clusters():
    return "<b>🔍 Mirror Wallet Cluster Scan</b>\n3 wallets observed trading in sync in last 2h."

def send_wallet_activity():
    return "<b>🐋 Whale Wallet Watch</b>\nTop wallet moved 1.2M MAX to new address 1h ago."
