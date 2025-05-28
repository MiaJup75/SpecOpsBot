import logging
from db import get_user_limits, log_trade, get_daily_trade_volume
from wallet import Wallet

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self):
        self.wallet = Wallet()

    def execute_sell(self, user_id: str, token_symbol: str, amount: float, price: float) -> bool:
        """Execute a sell order with trade limit checks and logging."""
        # Fetch user limits
        limits = get_user_limits(user_id)
        daily_limit = limits.get("daily_sell_limit", None)
        stop_loss_pct = limits.get("stop_loss_pct", None)

        # Check daily trade volume limit
        volume_today = get_daily_trade_volume(user_id, token_symbol)
        if daily_limit is not None and volume_today + amount > daily_limit:
            logger.warning(f"User {user_id} exceeded daily sell limit for {token_symbol}.")
            return False

        # Check stop loss condition - example only, depends on stored average buy price
        if stop_loss_pct is not None:
            avg_buy_price = self.get_avg_buy_price(user_id, token_symbol)
            if price < avg_buy_price * (1 - stop_loss_pct / 100):
                logger.warning(f"User {user_id} triggered stop loss for {token_symbol}.")
                # Could auto-trigger sell or alert user here
                return False

        # Execute the sell through Wallet
        try:
            success = self.wallet.swap_token(token_symbol, amount)
            if success:
                log_trade(user_id, token_symbol, "sell", amount, price)
                logger.info(f"Executed sell for user {user_id}: {amount} {token_symbol} @ {price}")
                return True
            else:
                logger.error(f"Wallet failed to execute sell for {token_symbol}")
                return False
        except Exception as e:
            logger.error(f"Error executing sell for user {user_id}: {e}")
            return False

    def get_avg_buy_price(self, user_id: str, token_symbol: str) -> float:
        # Placeholder for average buy price retrieval from DB or calculation
        # TODO: Implement this method properly
        return 0.000025  # Dummy value
