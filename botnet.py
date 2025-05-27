import os
import requests
from telegram import Bot
import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

# Thresholds for suspicious activity (example values)
VOLUME_SPIKE_THRESHOLD = 10_000_000  # USD volume spike in 24h
SELL_WHALE_THRESHOLD = 500_000  # tokens sold within short period

def fetch_token_activity(pair_id):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_id}"
    try:
        r = requests.get(url, timeout=5)
        return r.json().get("pair", {})
    except Exception as e:
        print(f"[Botnet] Error fetching token activity for {pair_id}: {e}")
        return {}

def detect_botnet_activity(token_symbol, pair_id):
    data = fetch_token_activity(pair_id)
    volume_24h = data.get("volume", {}).get("h24", 0)
    sells_24h = data.get("txns", {}).get("h24", {}).get("sells", 0)

    alerts = []

    if volume_24h > VOLUME_SPIKE_THRESHOLD:
        alerts.append(f"🚨 Volume spike detected: ${volume_24h:,.0f} in last 24h for {token_symbol}")

    if sells_24h > SELL_WHALE_THRESHOLD:
        alerts.append(f"⚠️ Whale sell detected: {sells_24h} tokens sold in last 24h for {token_symbol}")

    return alerts

def botnet_alerts(bot):
    # List of tokens to monitor — ideally dynamic
    monitored_tokens = {
        "MAX": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc",
        # Add more token symbol: pair_id here
    }

    for symbol, pair_id in monitored_tokens.items():
        alerts = detect_botnet_activity(symbol, pair_id)
        for alert in alerts:
            try:
                bot.send_message(chat_id=CHAT_ID, text=alert, parse_mode="HTML")
                print(f"[Botnet] Alert sent: {alert}")
            except Exception as e:
                print(f"[Botnet] Failed to send alert: {e}")
