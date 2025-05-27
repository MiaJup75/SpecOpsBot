import logging
import os
import requests
from db import get_tokens

logger = logging.getLogger(__name__)
CHAT_ID = os.getenv("CHAT_ID")

# Default target prices if not set per token
DEFAULT_TARGET_PRICE = 0.00005

def check_price_alerts(bot):
    """
    Checks tracked tokens for price target alerts.
    """
    tokens = get_tokens()
    for symbol in tokens:
        try:
            symbol_lower = symbol.lower()
            # Fetch pair address or use override from DB/config if implemented
            pair_address = get_pair_address_for_token(symbol)  # Implement this helper if you want

            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            pair_data = data.get("pair", {})

            price = float(pair_data.get("priceUsd", 0))
            target_price = get_target_price_for_token(symbol) or DEFAULT_TARGET_PRICE  # implement getter if needed

            if price >= target_price:
                msg = (
                    f"🔔 <b>Price Alert:</b> ${symbol} reached target price ${target_price:.6f}\n"
                    f"Current Price: ${price:.6f}"
                )
                logger.info(f"Price alert for {symbol} at price {price}")
                bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Error checking price alert for {symbol}: {e}")
