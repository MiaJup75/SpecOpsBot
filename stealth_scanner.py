import os
import requests
import datetime

from telegram import Bot

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

LAUNCH_LOOKBACK_MINUTES = 30
MIN_LP_USD = 10000  # Only alert if liquidity pool > $10K

def fetch_new_pairs():
    """Fetch newly created Solana token pairs from Dexscreener API."""
    url = "https://api.dexscreener.com/latest/dex/tokens/solana"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data.get("pairs", [])
    except Exception as e:
        print(f"[StealthScanner] Error fetching pairs: {e}")
        return []

def filter_stealth_launches(pairs):
    """Filter pairs launched within last 30 mins with low social signals (placeholder)."""
    now = datetime.datetime.utcnow()
    suspicious = []

    for pair in pairs:
        created_ts = pair.get("pairCreatedAt")
        if not created_ts:
            continue
        created_dt = datetime.datetime.utcfromtimestamp(created_ts / 1000)
        age_min = (now - created_dt).total_seconds() / 60

        lp_usd = pair.get("liquidity", {}).get("usd", 0)

        # Placeholder for social signals (can add real check later)
        social_mentions = 0

        if age_min <= LAUNCH_LOOKBACK_MINUTES and lp_usd >= MIN_LP_USD and social_mentions < 3:
            suspicious.append(pair)

    return suspicious

def send_stealth_alert(pair):
    """Send Telegram alert for stealth launch."""
    name = pair.get("name", "Unknown")
    symbol = pair.get("baseToken", {}).get("symbol", "UNK")
    lp = pair.get("liquidity", {}).get("usd", 0)
    created_ts = pair.get("pairCreatedAt", 0)
    created_dt = datetime.datetime.utcfromtimestamp(created_ts / 1000).strftime('%Y-%m-%d %H:%M:%S')

    message = (
        f"🚨 <b>Stealth Launch Detected</b> 🚨\n\n"
        f"Token: <b>{name} ({symbol})</b>\n"
        f"Liquidity: ${lp:,.0f}\n"
        f"Launched: {created_dt} UTC\n"
        f"<a href='https://dexscreener.com/solana/{pair.get('id')}'>View on Dexscreener</a>"
    )
    try:
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML", disable_web_page_preview=False)
        print(f"[StealthScanner] Alert sent for {symbol}")
    except Exception as e:
        print(f"[StealthScanner] Failed to send alert: {e}")

def scan_new_tokens(bot):
    pairs = fetch_new_pairs()
    suspicious = filter_stealth_launches(pairs)
    for pair in suspicious:
        send_stealth_alert(pair)
