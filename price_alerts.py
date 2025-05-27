import os
import requests
from db import get_tokens

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PRICE_TARGETS = {
    # Example: "TOKEN_SYMBOL": {"buy": 0.00002, "sell": 0.00005}
    "MAX": {"sell": 0.00005},
    # Add more as needed
}

def get_token_price(pair_id):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_id}"
    try:
        r = requests.get(url, timeout=5)
        pair = r.json().get("pair", {})
        return float(pair.get("priceUsd", 0))
    except Exception as e:
        print(f"[PriceAlerts] Error fetching price for {pair_id}: {e}")
        return 0

def check_price_triggers(bot):
    tokens = get_tokens()
    for symbol in tokens:
        symbol = symbol.upper()
        target = PRICE_TARGETS.get(symbol)
        if not target:
            continue

        # For demo, using hardcoded pair mapping; ideally load from config/db
        pair_id = {
            "MAX": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        }.get(symbol)

        if not pair_id:
            continue

        price = get_token_price(pair_id)
        if price == 0:
            continue

        if "sell" in target and price >= target["sell"]:
            msg = f"📢 <b>Price Alert:</b> {symbol} has reached SELL target price ${price:.6f}!"
            bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
            print(f"[PriceAlerts] Sell alert sent for {symbol} at {price}")

        # Add buy target alert logic similarly if desired
