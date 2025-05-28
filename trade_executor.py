import logging
from db import get_user_limits, log_trade
from wallet import Wallet

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.wallet = Wallet()
        self.limits = get_user_limits(user_id)

        # Defaults if not set
        self.daily_sell_limit = self.limits.get("daily_sell_limit", 1000.0)  # Example default $1000
        self.stop_loss_pct = self.limits.get("stop_loss_pct", 0.10)  # Example 10% stop loss

    def can_sell(self, token_symbol: str, amount: float, price: float) -> bool:
        # Here implement your daily sell limit check logic (simplified)
        # For demo, assume user can sell if amount * price < daily limit
        sell_value = amount * price
        if sell_value > self.daily_sell_limit:
            logger.warning(f"Sell amount ${sell_value} exceeds daily limit ${self.daily_sell_limit}")
            return False
        return True

    def execute_sell(self, token_symbol: str, amount: float, price: float) -> bool:
        if not self.can_sell(token_symbol, amount, price):
            logger.info(f"User {self.user_id} attempted sell over limit; aborted")
            return False

        # Add your wallet swap logic here; for now we simulate
        success = self.wallet.swap_token(token_symbol, amount)
        if success:
            log_trade(self.user_id, token_symbol, "SELL", amount, price)
            logger.info(f"Executed sell for user {self.user_id}: {amount} {token_symbol} at ${price}")
            return True
        else:
            logger.error(f"Sell failed for user {self.user_id}: {amount} {token_symbol} at ${price}")
            return False

    def auto_sell_if_target_reached(self, token_symbol: str, current_price: float):
        # Example auto-sell logic based on price target or stop loss
        target_price = self.limits.get("target_price")
        if target_price and current_price >= target_price:
            # Fetch user holdings amount from wallet or DB (stubbed here)
            amount_to_sell = 10  # Example amount
            price = current_price
            return self.execute_sell(token_symbol, amount_to_sell, price)
        # Implement stop-loss or other triggers similarly
        return False
