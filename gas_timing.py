import os
import logging
from solana.rpc.api import Client
from telegram import Bot

logger = logging.getLogger(__name__)

_last_mev_check = 0
MEV_CHECK_INTERVAL = 300  # 5 minutes

def fetch_gas_price():
    try:
        client = Client(os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"))
        resp = client.get_recent_blockhash()
        fee_calculator = resp['result']['value']['feeCalculator']
        lamports_per_signature = fee_calculator.get('lamportsPerSignature', 0)
        return lamports_per_signature
    except Exception as e:
        logger.error(f"[GasTiming] Error fetching gas price from RPC: {e}")
        return None

def check_mev_conditions():
    global _last_mev_check
    import time
    now = time.time()

    if now - _last_mev_check < MEV_CHECK_INTERVAL:
        return False  # Cache last result for efficiency

    _last_mev_check = now
    try:
        # TODO: Implement real MEV risk logic or API integration here
        # Placeholder returns False for no risk
        return False
    except Exception as e:
        logger.error(f"[GasTiming] Error checking MEV conditions: {e}")
        return False

def check_gas_and_mev(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    gas_price = fetch_gas_price()
    mev_risk = check_mev_conditions()

    msg_lines = ["⛽ <b>Gas & MEV Monitor</b>"]

    if gas_price is not None:
        msg_lines.append(f"Current Gas Price: {gas_price} lamports")

    if mev_risk:
        msg_lines.append("⚠️ MEV risk detected! Consider delaying transactions.")
    else:
        msg_lines.append("✅ MEV risk minimal.")

    message = "\n".join(msg_lines)
    bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
