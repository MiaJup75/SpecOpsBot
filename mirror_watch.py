import requests
import os
import logging
from db import get_wallets, get_wallet_last_tx, update_wallet_last_tx
from telegram import Bot
from time import time

logger = logging.getLogger(__name__)

ALERT_COOLDOWN_SECONDS = 1800  # 30 minutes cooldown per wallet

_last_alert_times = {}

def fetch_wallet_activity(address):
    url = f"https://public-api.solscan.io/account/tokens?account={address}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"[MirrorWatch] Error fetching wallet {address}: {e}")
        return None

def should_alert(wallet_label):
    now = time()
    last_alert = _last_alert_times.get(wallet_label)
    if last_alert and now - last_alert < ALERT_COOLDOWN_SECONDS:
        return False
    _last_alert_times[wallet_label] = now
    return True

def check_mirror_wallets(bot: Bot):
    wallets = get_wallets()
    chat_id = os.getenv("CHAT_ID")

    for label, address in wallets:
        try:
            data = fetch_wallet_activity(address)
            if data is None:
                continue
            
            # Extract last transaction signature or timestamp (customize based on API response)
            txs = data.get("data", [])
            if not txs:
                continue

            latest_tx = txs[0].get("signature") or txs[0].get("txHash") or ""
            if not latest_tx:
                continue
            
            last_known_tx = get_wallet_last_tx(address)
            if latest_tx == last_known_tx:
                continue  # No new tx

            if not should_alert(label):
                continue  # Cooldown active

            # Save latest tx
            update_wallet_last_tx(address, latest_tx)

            # Basic message construction
            msg = (
                f"🔍 Wallet Mirror Alert: '{label}' ({address[:6]}...{address[-6:]})\n"
                f"New activity detected: {latest_tx}\n"
                f"View on Solscan: https://solscan.io/tx/{latest_tx}"
            )
            bot.send_message(chat_id=chat_id, text=msg)

        except Exception as e:
            logger.error(f"[MirrorWatch] Failed processing wallet {address}: {e}")
