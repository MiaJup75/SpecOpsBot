import logging
import os
from db import get_user_limits, log_trade
from wallet import Wallet

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self):
        self.wallet = Wallet()
        self.max_daily_spend = float(os.getenv("MAX_DAILY_SPEND", "1000"))  # USD or token value limit
        self.trades_today = 0  # Track amount sold today (can be improved with persistent tracking)
        self.user_limits_cache = {}  # Cache user limits keyed by user_id

    def can_execute_sell(self, user_id: str, token_symbol: str, amount: float, price: float) -> bool:
        # Fetch user limits from DB or cache
        limits = self.user_limits_cache.get(user_id)
        if not limits:
            limits = get_user_limits(user_id)
            self.user_limits_cache[user_id] = limits

        daily_limit = limits.get("daily_sell_limit")
        stop_loss_pct = limits.get("stop_loss_pct")

        # Check daily sell limit
        if daily_limit is not None and (self.trades_today + amount * price) > daily_limit:
            logger.info(f"User {user_id} exceeded daily sell limit.")
            return False

        # TODO: Implement stop loss logic with historical purchase price comparison

        return True

    def execute_sell(self, user_id: str, token_symbol: str, amount: float, price: float) -> bool:
        if not self.can_execute_sell(user_id, token_symbol, amount, price):
            logger.warning(f"Trade denied for user {user_id} on {token_symbol}: Limits exceeded.")
            return False

        try:
            # Attempt to swap token to SOL or other base currency using wallet.swap_token
            success = self.wallet.swap_token(token_symbol, amount)
            if success:
                logger.info(f"Trade executed: User {user_id} sold {amount} {token_symbol} at price {price}")
                log_trade(user_id, token_symbol, "sell", amount, price)
                self.trades_today += amount * price
                return True
            else:
                logger.error(f"Swap failed for user {user_id} selling {token_symbol}")
                return False
        except Exception as e:
            logger.error(f"Exception during trade execution: {e}")
            return False

    def reset_daily_trades(self):
        # Reset daily trade counters - should be called by a daily scheduler job
        self.trades_today = 0
        self.user_limits_cache.clear()
        logger.info("Daily trades reset.")
