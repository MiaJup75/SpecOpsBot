import os
import requests
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

SOLSCAN_GAS_API = "https://public-api.solscan.io/gas-fees/recent"  # Example, replace if needed

def fetch_recent_gas_prices():
    try:
        response = requests.get(SOLSCAN_GAS_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        avg_fee = data.get("averageFee", None)
        max_fee = data.get("maxFee", None)
        min_fee = data.get("minFee", None)
        return avg_fee, max_fee, min_fee
    except Exception as e:
        logger.error(f"[GasTiming] Failed to fetch gas prices: {e}")
        return None, None, None

def check_mev_conditions():
    # TODO: Implement real MEV risk detection logic or API integration
    # For example, monitor tx mempool congestion, frontrunner patterns, etc.
    # For now, return False (no MEV risk)
    return False

def check_gas_and_mev(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    avg_fee, max_fee, min_fee = fetch_recent_gas_prices()
    mev_risk = check_mev_conditions()

    msg_lines = ["⛽ <b>Gas & MEV Monitor</b>"]

    if avg_fee is not None:
        msg_lines.append(f"Average Gas Fee: {avg_fee} lamports")
        msg_lines.append(f"Max Gas Fee: {max_fee} lamports")
        msg_lines.append(f"Min Gas Fee: {min_fee} lamports")
    else:
        msg_lines.append("⚠️ Unable to fetch gas price data.")

    if mev_risk:
        msg_lines.append("⚠️ MEV risk detected! Consider delaying transactions.")
    else:
        msg_lines.append("✅ MEV risk minimal.")

    message = "\n".join(msg_lines)
    bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
