import os
import requests
import datetime
from telegram import Bot
from db import get_wallets

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

# Whitelist of wallet labels to mirror (can be all or filtered)
WHITELISTED_LABELS = None  # None means all watched wallets are mirrored

def fetch_wallet_activity(address):
    url = f"https://public-api.solscan.io/account/transactions?account={address}&limit=5"
    try:
        res = requests.get(url, timeout=10)
        return res.json()
    except Exception as e:
        print(f"[MirrorWatch] Error fetching activity for {address}: {e}")
        return []

def detect_new_buys_sells(transactions, last_checked_time):
    buys = []
    sells = []
    for tx in transactions:
        block_time = tx.get("blockTime")
        if not block_time or block_time <= last_checked_time:
            continue
        # Simplified detection logic: scan tx details for token buy/sell
        # Real implementation needs decoding transaction instructions
        # For now, assume any SOL transfer in/out is buy/sell indicator

        # Example placeholders
        if "buy" in tx.get("memo", "").lower():
            buys.append(tx)
        if "sell" in tx.get("memo", "").lower():
            sells.append(tx)

    return buys, sells

def send_mirror_alert(label, address, tx_type, tx):
    msg = (f"👥 <b>Mirror Wallet Alert</b>\n"
           f"Wallet: {label}\n"
           f"Address: {address}\n"
           f"Action: {tx_type}\n"
           f"Tx Signature: {tx.get('signature')}\n"
           f"Time: {datetime.datetime.utcfromtimestamp(tx.get('blockTime')).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
           f"<a href='https://solscan.io/tx/{tx.get('signature')}'>View on Solscan</a>")
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML", disable_web_page_preview=False)
        print(f"[MirrorWatch] Alert sent for {label} {tx_type}")
    except Exception as e:
        print(f"[MirrorWatch] Failed to send alert: {e}")

def mirror_wallets(bot, last_checked_time):
    wallets = get_wallets()
    for label, address in wallets:
        if WHITELISTED_LABELS and label not in WHITELISTED_LABELS:
            continue
        txs = fetch_wallet_activity(address)
        buys, sells = detect_new_buys_sells(txs, last_checked_time)
        for tx in buys:
            send_mirror_alert(label, address, "BUY", tx)
        for tx in sells:
            send_mirror_alert(label, address, "SELL", tx)
