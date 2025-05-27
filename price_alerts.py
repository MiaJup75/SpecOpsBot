import logging
import os
import requests

logger = logging.getLogger(__name__)
CHAT_ID = os.getenv("CHAT_ID")

# Example price alert targets; in practice, store user configs in DB
PRICE_ALERTS = {
    "BONK": 0.0001,
    "MEOW": 0.00005,
    "CHAD": 0.0002,
}

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens/solana"

def check_price_alerts(bot):
    """
    Checks current prices against alert thresholds and notifies users.
    """
    for symbol, target in PRICE_ALERTS.items():
        try:
            url = f"{DEXSCREENER_API}/{symbol.lower()}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            price = float(data.get("priceUsd", 0))

            if price >= target:
                message = f"🔔 <b>Price Alert:</b> ${symbol} has reached target price ${target}\n" \
                          f"Current price: ${price:.6f}"
                logger.info(f"Price Alert triggered for {symbol} at price {price}")
                bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Error checking price alert for {symbol}: {e}")
