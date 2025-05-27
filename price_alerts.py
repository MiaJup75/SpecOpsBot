import os
import requests
from db import get_tokens  # Your tracked tokens list
from telegram import Bot

# Example token config with default targets
TOKEN_CONFIG = {
    "MAX": {
        "pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc",
        "target": 0.00005,  # Default target price in USD
    },
    # Add more tokens here with pair address and default target price
}

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
        config = TOKEN_CONFIG.get(token_upper)
        if not config:
            continue
        pair = config["pair"]
        target = config["target"]
        price = fetch_price(pair)
        if price is None:
            continue
        if price >= target:
            msg = (f"🚨 Price Target Hit for ${token_upper}!\n"
                   f"Current Price: ${price:.6f}\n"
                   f"Target Price: ${target:.6f}\n"
                   f"Consider reviewing your position.")
            bot.send_message(chat_id=chat_id, text=msg)
