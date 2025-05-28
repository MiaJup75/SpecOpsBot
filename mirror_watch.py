import requests
import os
import logging
from db import get_wallets
from telegram import Bot
import time

logger = logging.getLogger(__name__)

# Throttle alerts per wallet address
_last_alert_times = {}
ALERT_COOLDOWN_SECONDS = 1800  # 30 minutes cooldown

def can_alert(address: str) -> bool:
    now = time.time()
    last_alert = _last_alert_times.get(address)
    if last_alert and now - last_alert < ALERT_COOLDOWN_SECONDS:
        return False
    _last_alert_times[address] = now
    return True

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
            if not can_alert(address):
                continue  # Skip alert if in cooldown period

            activity = fetch_wallet_activity(address)
            # TODO: Add real detection logic for buys/sells here

            msg = f"🔍 Checked wallet '{label}' ({address[:6]}...{address[-6:]}) - Recent activity found."
            bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logger.error(f"[MirrorWatch] Failed to process wallet {address}: {e}")
