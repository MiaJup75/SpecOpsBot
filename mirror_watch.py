import requests
import os
from db import get_wallets
from telegram import Bot

def fetch_wallet_activity(address):
    # Example: fetch last transactions for the wallet from Solscan or other API
    url = f"https://public-api.solscan.io/account/tokens?account={address}"
    try:
        resp = requests.get(url, timeout=10)
        return resp.json()  # Adjust parsing as needed
    except Exception as e:
        print(f"[MirrorWatch] Error fetching wallet {address}: {e}")
        return []

def check_mirror_wallets(bot: Bot):
    wallets = get_wallets()
    chat_id = os.getenv("CHAT_ID")

    for label, address in wallets:
        activity = fetch_wallet_activity(address)
        # Placeholder: here you can implement logic to detect new buys/sells or interesting activity
        # For now, just notify that the wallet was checked
        msg = f"🔍 Checked wallet '{label}' ({address[:6]}...{address[-6:]}) - Recent activity found."
        bot.send_message(chat_id=chat_id, text=msg)
