import requests
import os
import logging
from db import get_wallets, get_wallet_activity_cache, update_wallet_activity_cache
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
        return None

def detect_activity_changes(old_activity, new_activity):
    # Implement comparison logic for buys/sells or balance changes
    # Return True if new meaningful activity detected
    if old_activity is None:
        return True  # first time fetch

    # Simplified example: check if token balances changed
    old_balances = {t['mint']: t['amount'] for t in old_activity.get('tokens', [])}
    new_balances = {t['mint']: t['amount'] for t in new_activity.get('tokens', [])}

    for mint, new_amt in new_balances.items():
        old_amt = old_balances.get(mint, "0")
        if new_amt != old_amt:
            return True
    return False

def check_mirror_wallets(bot: Bot):
    wallets = get_wallets()
    chat_id = os.getenv("CHAT_ID")

    for label, address in wallets:
        try:
            new_activity = fetch_wallet_activity(address)
            if new_activity is None:
                continue

            old_activity = get_wallet_activity_cache(address)
            if detect_activity_changes(old_activity, new_activity):
                msg = f"🔍 Wallet '{label}' ({address[:6]}...{address[-6:]}) has new activity."
                bot.send_message(chat_id=chat_id, text=msg)
                update_wallet_activity_cache(address, new_activity)
        except Exception as e:
            logger.error(f"[MirrorWatch] Failed to process wallet {address}: {e}")
