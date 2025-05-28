import logging
from db import get_user_limits, update_daily_spent, log_trade

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, user_id):
        self.user_id = user_id

    def can_execute_trade(self, trade_amount_usd):
        daily_limit, daily_spent = get_user_limits(self.user_id)
        if daily_spent + trade_amount_usd > daily_limit:
            return False, daily_limit, daily_spent
        return True, daily_limit, daily_spent

    def execute_buy(self, token_symbol, amount, price):
        trade_value = amount * price
        can_execute, limit, spent = self.can_execute_trade(trade_value)
        if not can_execute:
            logger.warning(f"User {self.user_id} exceeded daily limit. Trade blocked.")
            return False, f"Daily limit of ${limit} exceeded. Already spent: ${spent}."
        # Execute buy logic here (connect with wallet or exchange)
        update_daily_spent(self.user_id, trade_value)
        log_trade(self.user_id, "BUY", token_symbol, amount, price)
        logger.info(f"Executed buy: {amount} {token_symbol} at ${price} for user {self.user_id}")
        return True, f"Bought {amount} {token_symbol} at ${price}"

    def execute_sell(self, token_symbol, amount, price):
        trade_value = amount * price
        # Sell might not have a daily limit but log anyway
        update_daily_spent(self.user_id, trade_value)
        log_trade(self.user_id, "SELL", token_symbol, amount, price)
        logger.info(f"Executed sell: {amount} {token_symbol} at ${price} for user {self.user_id}")
        return True, f"Sold {amount} {token_symbol} at ${price}"
