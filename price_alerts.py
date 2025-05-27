from db import get_tokens
import requests
import os

def check_price_targets(bot):
    tokens = get_tokens()
    chat_id = os.getenv("CHAT_ID")
    for symbol in tokens:
        # Use TOKEN_OVERRIDES or default target price (example)
        target_price = 0.00005  # You can load from config or DB
        
        # Fetch current price from Dexscreener or similar
        try:
            # Replace with real pair address mapping for symbol
            pair = "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
            r = requests.get(url, timeout=5)
            price = float(r.json()['pair']['priceUsd'])
            if price >= target_price:
                msg = f"🎯 Token ${symbol} hit target price of ${target_price:.6f} (current: ${price:.6f})"
                bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            print(f"[PriceAlerts] Error fetching price for {symbol}: {e}")
