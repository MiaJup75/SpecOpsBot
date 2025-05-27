import os
import requests
from db import get_tokens
from telegram import Bot
import datetime

# Config: minimum LP threshold and time window in minutes
MIN_LP_USD = 10000
MAX_TOKEN_AGE_MIN = 30

def fetch_new_tokens():
    """Fetch tokens launched within the last MAX_TOKEN_AGE_MIN minutes from Dexscreener"""
    url = "https://api.dexscreener.com/latest/dex/tokens/solana"
    try:
        response = requests.get(url, timeout=10).json()
        tokens = response.get("tokens", [])
        recent_tokens = []
        cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=MAX_TOKEN_AGE_MIN)

        for token in tokens:
            # Parse launch time from timestamp (assume in seconds)
            launch_ts = token.get("launchTime") or token.get("createdAt") or 0
            if launch_ts:
                launch_dt = datetime.datetime.utcfromtimestamp(launch_ts)
                if launch_dt > cutoff_time:
                    recent_tokens.append(token)
        return recent_tokens
    except Exception as e:
        print(f"[stealth_launch] Error fetching new tokens: {e}")
        return []

def filter_tokens_by_lp(tokens, min_lp_usd=MIN_LP_USD):
    filtered = []
    for token in tokens:
        lp_usd = token.get("liquidityUSD") or 0
        if lp_usd >= min_lp_usd:
            filtered.append(token)
    return filtered

def scan_new_tokens(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    new_tokens = fetch_new_tokens()
    filtered_tokens = filter_tokens_by_lp(new_tokens)

    if not filtered_tokens:
        return

    for token in filtered_tokens:
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "???")
        lp_usd = token.get("liquidityUSD", 0)
        launch_time = token.get("launchTime", 0)
        launch_dt = datetime.datetime.utcfromtimestamp(launch_time).strftime('%Y-%m-%d %H:%M:%S') if launch_time else "Unknown"

        msg = (f"🚀 New Token Launch Detected!\n"
               f"Name: {name} (${symbol})\n"
               f"Liquidity: ${lp_usd:,.0f}\n"
               f"Launch Time (UTC): {launch_dt}\n"
               f"Check it out on Dexscreener!")

        try:
            bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            print(f"[stealth_launch] Failed to send Telegram message: {e}")
