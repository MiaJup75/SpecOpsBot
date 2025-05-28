import os
import requests
from telegram import Bot
import logging

logger = logging.getLogger(__name__)

SOLSCAN_GAS_API = "https://public-api.solscan.io/gas-fees/recent"

def fetch_gas_price():
    """
    Fetch recent Solana gas fees data from Solscan public API.
    Returns average gas fee in lamports or None on failure.
    """
    try:
        resp = requests.get(SOLSCAN_GAS_API, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        avg_fee = data.get("averageFee")
        return avg_fee
    except Exception as e:
        logger.error(f"[GasTiming] Error fetching gas price: {e}")
        return None

def check_mev_conditions():
    """
    Placeholder for MEV detection logic.
    Here you could add real API calls or heuristics.
    Returns True if MEV risk is detected, else False.
    """
    # Example logic: Check for sudden spikes, congestions, or frontrunning patterns
    return False

def check_gas_and_mev(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    avg_gas_fee = fetch_gas_price()
    mev_risk = check_mev_conditions()

    message_lines = ["⛽ <b>Gas & MEV Monitor</b>"]

    if avg_gas_fee is not None:
        message_lines.append(f"Current Average Gas Fee: {avg_gas_fee} lamports")
    else:
        message_lines.append("⚠️ Unable to fetch gas fee data.")

    if mev_risk:
        message_lines.append("⚠️ MEV risk detected! Consider delaying transactions.")
    else:
        message_lines.append("✅ MEV risk minimal.")

    message = "\n".join(message_lines)
    bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
