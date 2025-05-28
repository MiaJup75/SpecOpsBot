import logging
import os
from datetime import datetime, timedelta
from db import log_trade, get_user_limits, get_trade_history
from wallet import Wallet

logger = logging.getLogger(__name__)

wallet = Wallet()

# Constants for limits - could be fetched dynamically per user later
DEFAULT_DAILY_SELL_LIMIT = 10000  # Max USD to sell per day
DEFAULT_STOP_LOSS_PERCENT = 10  # 10% loss trigger

def execute_sell(token_symbol: str, amount: float, user_id: str) -> bool:
    """
    Execute a sell order with limit checks and logging.

    :param token_symbol: Symbol to sell, e.g. 'MAX'
    :param amount: Amount in tokens to sell
    :param user_id: Unique user identifier for limits
    :return: True if sell executed, False otherwise
    """

    try:
        # Step 1: Fetch user limits or use defaults
        user_limits = get_user_limits(user_id)
        daily_limit = user_limits.get("daily_sell_limit", DEFAULT_DAILY_SELL_LIMIT)
        stop_loss_pct = user_limits.get("stop_loss_pct", DEFAULT_STOP_LOSS_PERCENT)

        # Step 2: Check daily sell volume
        today = datetime.utcnow().date()
        trades_today = get_trade_history(user_id, token_symbol, start_date=today)
        total_sold_today = sum(t['amount'] for t in trades_today if t['side'] == 'sell')

        # Step 3: Check if amount exceeds remaining daily limit
        if total_sold_today + amount > daily_limit:
            logger.warning(f"Sell amount exceeds daily limit for user {user_id}.")
            return False

        # Step 4: Check current price and stop loss trigger (pseudo-code)
        # current_price = get_current_price(token_symbol)
        # avg_cost = get_average_cost(user_id, token_symbol)
        # if current_price < avg_cost * (1 - stop_loss_pct / 100):
        #     logger.info("Stop loss triggered, proceed to sell.")

        # Step 5: Execute the sell using Wallet swap_token method
        success = wallet.swap_token(token_symbol, amount)
        if not success:
            logger.error(f"Swap failed for {token_symbol}, amount: {amount}")
            return False

        # Step 6: Log the trade in DB
        log_trade(
            user_id=user_id,
            token_symbol=token_symbol,
            amount=amount,
            side="sell",
            price=None,  # can add price info if available
            timestamp=datetime.utcnow()
        )
        logger.info(f"Sell executed and logged for user {user_id}: {amount} {token_symbol}")
        return True

    except Exception as e:
        logger.error(f"Error executing sell for user {user_id}: {e}")
        return False
