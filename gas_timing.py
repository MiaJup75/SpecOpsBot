import os
import requests
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

SOLSCAN_GAS_API = "https://public-api.solscan.io/gas-fees/recent"

def fetch_recent_gas_prices():
    """Fetch recent Solana gas prices from Solscan API."""
    try:
        response = requests.get(SOLSCAN_GAS_API, timeout=5)
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
    """
    Placeholder for MEV risk detection logic.
    You can integrate more advanced heuristics or third-party APIs here.
    """
    # Example: If average gas fee > threshold or specific network conditions.
    return False

def check_gas_and_mev(bot: Bot):
    chat_id = os.getenv("CHAT_ID")
    avg_fee, max_fee, min_fee = fetch_recent_gas_prices()
    mev_risk = check_mev_conditions()

    if avg_fee is None:
        message = "⚠️ Unable to fetch gas price data currently."
    else:
        message_lines = [
            "⛽ <b>Solana Gas & MEV Monitor</b>",
            f"Average Fee: {avg_fee} lamports",
            f"Max Fee: {max_fee} lamports",
            f"Min Fee: {min_fee} lamports",
        ]
        if mev_risk:
            message_lines.append("⚠️ MEV risk detected! Consider delaying transactions.")
        else:
            message_lines.append("✅ MEV risk minimal.")

        message = "\n".join(message_lines)

    bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
