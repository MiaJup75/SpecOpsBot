import logging
from datetime import datetime
from db import get_user_limits, log_trade
from wallet import Wallet

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.wallet = Wallet()
        self.daily_max_spend, self.single_trade_max = get_user_limits(user_id)

    def execute_sell(self, token_symbol: str, amount: float, price: float) -> bool:
        """
        Execute a sell trade for the given token and amount at the given price.

        Returns True if successful, False otherwise.
        """
        total_value = amount * price
        logger.info(f"User {self.user_id} wants to sell {amount} {token_symbol} at price {price} (total ${total_value})")

        # Check limits
        if total_value > self.single_trade_max:
            logger.warning(f"Trade amount ${total_value} exceeds single trade max of ${self.single_trade_max}")
            return False

        # TODO: Check daily spent so far and enforce daily_max_spend limit (requires tracking daily sums)

        try:
            # Call wallet swap to sell token -> SOL (assuming token_symbol is being sold for SOL)
            success = self.wallet.swap_token(token_symbol, amount)
            if success:
                log_trade(self.user_id, token_symbol, amount, price, trade_type="SELL", timestamp=datetime.utcnow())
                logger.info(f"Trade executed and logged for user {self.user_id}")
                return True
            else:
                logger.error(f"Trade execution failed for user {self.user_id}")
                return False
        except Exception as e:
            logger.error(f"Exception during trade execution for user {self.user_id}: {e}")
            return False
