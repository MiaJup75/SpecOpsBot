import logging
from db import get_user_limits, log_trade
from wallet import Wallet
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger(__name__)

DB_NAME = "solmad.db"

def get_daily_spent(user_id: int) -> float:
    """Calculate total spent by user in last 24 hours."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    since = datetime.utcnow() - timedelta(days=1)
    c.execute('''
        SELECT SUM(amount * price) FROM trade_history
        WHERE user_id=? AND trade_type='SELL' AND timestamp >= ?
    ''', (user_id, since))
    result = c.fetchone()
    conn.close()
    return result[0] if result[0] is not None else 0.0

def execute_sell(user_id: int, token_symbol: str, amount: float, price: float) -> dict:
    """
    Executes a sell order for a user if within trade limits.
    Returns a dict with success status and message.
    """

    max_daily_spend, max_single_trade = get_user_limits(user_id)
    logger.info(f"User {user_id} limits - Daily max: {max_daily_spend}, Single max: {max_single_trade}")

    total_spent_today = get_daily_spent(user_id)
    trade_value = amount * price

    if trade_value > max_single_trade:
        msg = f"Trade value ${trade_value:.2f} exceeds your single trade max limit of ${max_single_trade:.2f}."
        logger.warning(msg)
        return {"success": False, "message": msg}

    if (total_spent_today + trade_value) > max_daily_spend:
        msg = f"Trade would exceed daily spend limit of ${max_daily_spend:.2f}. Already spent ${total_spent_today:.2f} today."
        logger.warning(msg)
        return {"success": False, "message": msg}

    try:
        wallet = Wallet()
        # For demo, we assume swap_token is used to sell tokens for SOL or stablecoin
        # Adjust logic as needed for real sell order via DEX or exchange API
        success = wallet.swap_token(token_symbol, amount)
        if not success:
            msg = "Swap execution failed."
            logger.error(msg)
            return {"success": False, "message": msg}

        log_trade(user_id, "SELL", token_symbol, amount, price)
        msg = f"Sell order executed: {amount} {token_symbol} at ${price:.4f}."
        logger.info(msg)
        return {"success": True, "message": msg}

    except Exception as e:
        logger.error(f"Error executing sell trade: {e}")
        return {"success": False, "message": "Unexpected error during trade execution."}
