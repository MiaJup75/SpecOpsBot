import logging
from db import get_user_limits, log_trade, get_daily_trade_volume
from wallet import Wallet

logger = logging.getLogger(__name__)
wallet = Wallet()

def execute_sell(user_id: str, token_symbol: str, amount: float, price: float) -> bool:
    """
    Executes a sell order with limit checks and logs the trade.
    Returns True if trade was successful, False otherwise.
    """

    # Check user limits
    limits = get_user_limits(user_id)
    daily_limit = limits.get("daily_sell_limit")
    stop_loss_pct = limits.get("stop_loss_pct")

    # Check daily sell limit
    if daily_limit is not None:
        daily_volume = get_daily_trade_volume(user_id, token_symbol)
        if daily_volume + amount > daily_limit:
            logger.warning(f"User {user_id} exceeded daily sell limit for {token_symbol}.")
            return False  # Exceeds daily limit

    # TODO: Implement stop loss price check (would require avg buy price tracking)
    # For now, just log a placeholder check
    if stop_loss_pct is not None:
        # Example: If current price is below stop loss threshold, do not sell
        # This requires average cost which is not implemented yet
        pass

    # Execute the sell swap via Wallet.swap_token
    try:
        success = wallet.swap_token(token_symbol, amount)
        if success:
            log_trade(user_id, token_symbol, "sell", amount, price)
            logger.info(f"Trade executed and logged: {user_id} sold {amount} {token_symbol} at {price}")
            return True
        else:
            logger.error(f"Swap failed for user {user_id} selling {token_symbol}")
            return False
    except Exception as e:
        logger.error(f"Exception during trade execution for user {user_id}: {e}")
        return False
