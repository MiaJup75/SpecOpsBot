import logging
from datetime import datetime, date
from db import log_trade, get_trade_history, get_user_limits

logger = logging.getLogger(__name__)

# Simulated external sell function (replace with real trade execution)
def execute_sell_order(token_symbol: str, amount: float) -> bool:
    logger.info(f"Executing sell order for {amount} {token_symbol}")
    # Integrate with exchange or DEX here
    return True  # Assume success for now

def can_sell(user_id: str, token_symbol: str, amount: float) -> bool:
    limits = get_user_limits(user_id)
    daily_limit = limits.get("daily_sell_limit", 10000)
    stop_loss_pct = limits.get("stop_loss_pct", 10)

    today = date.today()
    trades_today = get_trade_history(user_id, token_symbol, today)

    total_sold_today = sum(t['amount'] for t in trades_today if t['side'] == 'sell')

    if total_sold_today + amount > daily_limit:
        logger.warning(f"User {user_id} exceeded daily sell limit for {token_symbol}")
        return False
    # Implement stop-loss logic if price data is available
    # (e.g., compare current price with average buy price)

    return True

def execute_sell(user_id: str, token_symbol: str, amount: float, price: float | None = None):
    if not can_sell(user_id, token_symbol, amount):
        logger.info(f"Sell order blocked for user {user_id} on {token_symbol} amount {amount}")
        return False

    success = execute_sell_order(token_symbol, amount)
    if success:
        log_trade(user_id, token_symbol, amount, 'sell', price, datetime.utcnow())
        logger.info(f"Logged sell trade for user {user_id} on {token_symbol} amount {amount}")
        return True
    else:
        logger.error(f"Failed to execute sell for user {user_id} on {token_symbol}")
        return False
