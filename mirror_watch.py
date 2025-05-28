import requests
import os
import logging
from db import get_wallets
from telegram import Bot
from time import time

logger = logging.getLogger(__name__)

_last_checked = {}
ALERT_COOLDOWN_SECONDS = 1800  # 30 minutes cooldown per wallet

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
        now = time()
        last_time = _last_checked.get(address, 0)
        if now - last_time < ALERT_COOLDOWN_SECONDS:
            continue  # Skip if cooldown not passed

        try:
            activity = fetch_wallet_activity(address)
            # Example: check if token count or balances changed here
            # For MVP, just send a simple notification:
            msg = f"🔍 Checked wallet '{label}' ({address[:6]}...{address[-6:]}) - Activity detected."
            bot.send_message(chat_id=chat_id, text=msg)
            _last_checked[address] = now
        except Exception as e:
            logger.error(f"[MirrorWatch] Failed to process wallet {address}: {e}")
