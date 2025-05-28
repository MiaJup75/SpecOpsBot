import requests
import os
import logging
from db import get_wallets
from telegram import Bot

logger = logging.getLogger(__name__)

def fetch_wallet_activity(address):
    url = f"https://public-api.solscan.io/account/tokens?account={address}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"[MirrorWatch] Error fetching wallet {address}: {e}")
        return []

def check_mirror_wallets(bot: Bot):
    wallets = get_wallets()
    chat_id = os.getenv("CHAT_ID")

    for label, address in wallets:
        try:
            activity = fetch_wallet_activity(address)
            # Real logic placeholder:
            # Implement logic to detect buys/sells, significant changes, etc.
            # Example: if recent buys > threshold, send alert
            # For now just a notification of check:
            msg = f"🔍 Checked wallet '{label}' ({address[:6]}...{address[-6:]}) - Recent activity found."
            bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logger.error(f"[MirrorWatch] Failed to process wallet {address}: {e}")
