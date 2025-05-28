import requests
import os
import logging
from db import get_wallets, get_wallet_last_tx, update_wallet_last_tx
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
        return {}

def check_mirror_wallets(bot: Bot):
    wallets = get_wallets()
    chat_id = os.getenv("CHAT_ID")

    for label, address in wallets:
        try:
            activity = fetch_wallet_activity(address)
            if not activity:
                continue

            # Extract the latest transaction signature or timestamp (depends on API response)
            latest_tx = None
            # Assuming response has a list of recent transactions under 'transactions'
            txns = activity.get("transactions", [])
            if txns:
                latest_tx = txns[0].get("signature")

            last_tx = get_wallet_last_tx(address)
            if latest_tx and latest_tx != last_tx:
                msg = f"🔔 New activity on wallet '{label}' ({address[:6]}...{address[-6:]})."
                bot.send_message(chat_id=chat_id, text=msg)
                update_wallet_last_tx(address, latest_tx)

        except Exception as e:
            logger.error(f"[MirrorWatch] Failed to process wallet {address}: {e}")
