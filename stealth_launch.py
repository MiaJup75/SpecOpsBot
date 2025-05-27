import time
import requests
from token_config import get_token_config
from telegram import Bot
from db import get_tokens

SCANNED_TOKENS = set()

def fetch_new_token_pairs():
    # Example: fetch recently created token pairs on Solana
    url = "https://api.dexscreener.com/latest/dex/tokens?chain=solana"
    try:
        resp = requests.get(url, timeout=10).json()
        return resp.get("tokens", [])
    except Exception as e:
        print(f"[StealthLaunch] Failed to fetch tokens: {e}")
        return []

def scan_new_tokens(bot: Bot):
    new_pairs = fetch_new_token_pairs()
    chat_id = os.getenv("CHAT_ID")

    for token in new_pairs:
        symbol = token.get("symbol", "").upper()
        if symbol in SCANNED_TOKENS:
            continue

        config = get_token_config(symbol)
        social_signal = 0  # Implement social signal check or import it

        # Basic filtering - example logic
        if social_signal > 50:
            # skip tokens with high social signals (not stealthy)
            SCANNED_TOKENS.add(symbol)
            continue

        # Additional honeypot and contract checks can be added here

        message = f"🚀 New Token Launch Detected: ${symbol}\n"
        if config:
            message += f"Target Price: ${config.get('target_price', 'N/A')}\n"

        bot.send_message(chat_id=chat_id, text=message)
        SCANNED_TOKENS.add(symbol)
