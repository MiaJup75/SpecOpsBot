import requests
import os
import logging
from db import get_wallets
from telegram import Bot
from time import time

logger = logging.getLogger(__name__)

# Track last activity timestamps to avoid duplicate alerts
_last_activity_timestamp = {}

def fetch_wallet_activity(address):
    url = f"https://public-api.solscan.io/account/tokens?account={address}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"[MirrorWatch] Error fetching wallet {address}: {e}")
        return []

def detect_new_activity(wallet_label, address, activity):
    """
    Analyze the wallet's token activity and detect new buys/sells.
    This is a simplified example: expand with actual parsing of transaction details.
    """
    now = time()
    last_time = _last_activity_timestamp.get(address, 0)

    # Suppose activity has a 'lastUpdated' timestamp (mocked here)
    last_updated = activity.get("lastUpdated", now)  # Use current time if not present

    if last_updated > last_time:
        _last_activity_timestamp[address] = last_updated
        # Here, analyze activity details for buys/sells - simplified:
        return True, f"New activity detected for wallet '{wallet_label}' ({address[:6]}...{address[-6:]})"
    return False, ""

def check_mirror_wallets(bot: Bot):
    wallets = get_wallets()
    chat_id = os.getenv("CHAT_ID")

    for label, address in wallets:
        try:
            activity = fetch_wallet_activity(address)
            if not activity:
                continue

            has_new_activity, msg = detect_new_activity(label, address, activity)
            if has_new_activity:
                bot.send_message(chat_id=chat_id, text=f"🔍 {msg}")
        except Exception as e:
            logger.error(f"[MirrorWatch] Failed to process wallet {address}: {e}")
