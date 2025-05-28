import os
import requests
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

def fetch_wallet_transactions(address, limit=10):
    """Fetch recent transactions for a wallet from Solscan API."""
    url = f"https://public-api.solscan.io/account/transactions?account={address}&limit={limit}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"[MirrorWatch] Error fetching txs for wallet {address}: {e}")
        return []

def parse_new_buys_sells(tx_list, last_checked_signature=None):
    """
    Parse transactions to detect buys and sells.
    This is a simplified heuristic checking for token transfer direction and amount.
    last_checked_signature is used to avoid repeat alerts on old txs.
    """
    events = []
    for tx in reversed(tx_list):  # oldest first to newest
        sig = tx.get("txHash")
        if sig == last_checked_signature:
            break  # reached previously processed txs

        instructions = tx.get("innerInstructions", [])
        # Simplified: look for token transfers and amounts in instructions
        for instr in instructions:
            for ix in instr.get("instructions", []):
                if ix.get("program") == "spl-token":
                    parsed = ix.get("parsed", {})
                    info = parsed.get("info", {})
                    amount = int(info.get("amount", 0))
                    if amount > 0:
                        # Use logic to differentiate buy or sell depending on source/destination
                        src = info.get("source")
                        dst = info.get("destination")
                        # Example logic: if destination is this wallet, it's a buy
                        if dst and dst.lower() == tx.get("account", "").lower():
                            events.append(("buy", amount, sig))
                        elif src and src.lower() == tx.get("account", "").lower():
                            events.append(("sell", amount, sig))
    return events

# Store last seen signature per wallet to avoid duplicate alerts
_last_seen_signature = {}

def check_mirror_wallets(bot: Bot):
    wallets = [] 
    try:
        from db import get_wallets
        wallets = get_wallets()
    except Exception as e:
        logger.error(f"[MirrorWatch] Failed loading wallets from DB: {e}")
        return

    chat_id = os.getenv("CHAT_ID")
    for label, address in wallets:
        try:
            txs = fetch_wallet_transactions(address)
            if not txs:
                continue
            last_sig = _last_seen_signature.get(address)
            events = parse_new_buys_sells(txs, last_checked_signature=last_sig)
            if events:
                for event_type, amount, sig in events:
                    action = "bought" if event_type == "buy" else "sold"
                    msg = (
                        f"🔔 Wallet '{label}' {action} {amount} tokens.\n"
                        f"Wallet: <code>{address}</code>\n"
                        f"Tx Signature: <a href='https://solscan.io/tx/{sig}'>View Tx</a>"
                    )
                    bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")
                # Update last seen tx signature
                _last_seen_signature[address] = events[-1][2]

        except Exception as e:
            logger.error(f"[MirrorWatch] Error processing wallet {address}: {e}")
