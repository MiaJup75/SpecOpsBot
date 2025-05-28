import os
import requests
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

SOLSCAN_GAS_API = "https://public-api.solscan.io/gas-fees/recent"

def fetch_gas_price():
    try:
        response = requests.get(SOLSCAN_GAS_API, timeout=5)
        response.raise_for_status()
        data = response.json()
        # Adjust field names depending on actual API response
        avg_fee = data.get("averageFee")
        max_fee = data.get("maxFee")
        min_fee = data.get("minFee")
        return avg_fee, max_fee, min_fee
    except Exception as e:
        logger.error(f"[GasTiming] Failed to fetch gas prices: {e}")
        return None, None, None

def check_mev_conditions():
    # Placeholder for advanced MEV detection, can integrate third-party APIs later
    return False

def check_gas_and_mev(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    avg_fee, max_fee, min_fee = fetch_gas_price()
    mev_risk = check_mev_conditions()

    if avg_fee is None:
        bot.send_message(chat_id=chat_id, text="⚠️ Unable to fetch gas fee data at this time.")
        return

    msg_lines = [
        "⛽ <b>Solana Gas & MEV Monitor</b>",
        f"Average Fee: {avg_fee} lamports",
        f"Max Fee: {max_fee} lamports",
        f"Min Fee: {min_fee} lamports",
    ]

    if mev_risk:
        msg_lines.append("⚠️ MEV risk detected! Consider delaying transactions.")
    else:
        msg_lines.append("✅ MEV risk minimal.")

    message = "\n".join(msg_lines)
    bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
