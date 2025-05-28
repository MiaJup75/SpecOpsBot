import logging
from datetime import datetime
from db import log_trade, get_user_limits, get_trade_history
from wallet import Wallet

logger = logging.getLogger(__name__)
wallet = Wallet()

DEFAULT_DAILY_SELL_LIMIT = 10000  # USD
DEFAULT_STOP_LOSS_PERCENT = 10  # Percent

def execute_sell(token_symbol: str, amount: float, user_id: str) -> bool:
    try:
        user_limits = get_user_limits(user_id)
        daily_limit = user_limits.get("daily_sell_limit", DEFAULT_DAILY_SELL_LIMIT)
        stop_loss_pct = user_limits.get("stop_loss_pct", DEFAULT_STOP_LOSS_PERCENT)

        today = datetime.utcnow().date()
        trades_today = get_trade_history(user_id, token_symbol, start_date=today)
        total_sold_today = sum(t['amount'] for t in trades_today if t['side'] == 'sell')

        if total_sold_today + amount > daily_limit:
            logger.warning(f"User {user_id} exceeded daily sell limit.")
            return False

        # TODO: Add stop loss price check here if available

        success = wallet.swap_token(token_symbol, amount)
        if not success:
            logger.error(f"Swap failed for {token_symbol} amount {amount}")
            return False

        log_trade(
            user_id=user_id,
            token_symbol=token_symbol,
            amount=amount,
            side="sell",
            price=None,
            timestamp=datetime.utcnow()
        )
        logger.info(f"Sell executed for user {user_id}: {amount} {token_symbol}")
        return True
    except Exception as e:
        logger.error(f"Error executing sell: {e}")
        return False
