import os
import requests
from db import get_tokens  # Your tracked tokens list
from telegram import Bot
from token_config import get_token_config

def fetch_price(pair):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
    try:
        response = requests.get(url, timeout=5).json()
        price = float(response.get("pair", {}).get("priceUsd", 0))
        return price
    except Exception as e:
        print(f"[PriceAlerts] Failed to fetch price for {pair}: {e}")
        return None

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
        if price >= target:
            msg = (f"🚨 Price Target Hit for ${token_upper}!\n"
                   f"Current Price: ${price:.6f}\n"
                   f"Target Price: ${target:.6f}\n"
                   f"Consider reviewing your position.")
            bot.send_message(chat_id=chat_id, text=msg)
