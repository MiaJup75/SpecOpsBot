import os
import requests
import time
from telegram import Bot
from db import get_tokens
from token_config import get_token_config
import logging

logger = logging.getLogger(__name__)

# Track last alert times per token to avoid spamming
_alerted_tokens = {}
ALERT_COOLDOWN_SECONDS = 1800  # 30 minutes cooldown between alerts per token

def fetch_price(pair):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
    try:
        response = requests.get(url, timeout=5).json()
        price = float(response.get("pair", {}).get("priceUsd", 0))
        return price
    except Exception as e:
        logger.error(f"[PriceAlerts] Failed to fetch price for {pair}: {e}")
        return None

def should_alert(token_symbol):
    now = time.time()
    last_alert = _alerted_tokens.get(token_symbol)
    if last_alert and now - last_alert < ALERT_COOLDOWN_SECONDS:
        return False
    _alerted_tokens[token_symbol] = now
    return True

def check_price_targets(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    tokens = get_tokens()
    for token in tokens:
        token_upper = token.upper()
        config = get_token_config(token_upper)
        if not config:
            continue
        pair = config.get("pair")
        target = config.get("target_price")
        if not pair or target is None:
            continue
        price = fetch_price(pair)
        if price is None:
            continue
        if price >= target and should_alert(token_upper):
            msg = (f"🚨 Price Target Hit for ${token_upper}!\n"
                   f"Current Price: ${price:.6f}\n"
                   f"Target Price: ${target:.6f}\n"
                   f"Consider reviewing your position.")
            bot.send_message(chat_id=chat_id, text=msg)
