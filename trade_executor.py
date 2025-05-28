import logging
import time
from typing import Optional
from wallet import Wallet
from db import log_trade, get_daily_trade_volume, get_user_trade_limits

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, wallet: Wallet, cooldown_seconds=60):
        self.wallet = wallet
        self.cooldown_seconds = cooldown_seconds
        self.last_trade_time = 0

    def can_trade(self) -> bool:
        """Check if cooldown period passed for next trade."""
        elapsed = time.time() - self.last_trade_time
        if elapsed < self.cooldown_seconds:
            logger.debug(f"Cooldown active: {elapsed:.1f}s elapsed, need {self.cooldown_seconds}s")
            return False
        return True

    def check_trade_limits(self, user_id: Optional[int], amount_sol: float) -> bool:
        """
        Check user daily limits and overall trade limits.
        Replace or extend with your actual logic.

        Returns True if trade is allowed.
        """
        if user_id is None:
            # If no user tracking, allow by default
            return True

        daily_volume = get_daily_trade_volume(user_id)
        max_daily = get_user_trade_limits(user_id).get("max_daily_sol", 10.0)  # example max 10 SOL daily

        if daily_volume + amount_sol > max_daily:
            logger.warning(f"User {user_id} exceeds daily limit: {daily_volume + amount_sol:.2f} SOL > {max_daily}")
            return False
        return True

    def execute_buy(self, token_symbol: str, amount_sol: float, user_id: Optional[int] = None, max_slippage_bps=50) -> bool:
        """Execute buy order for a token with checks and logging."""
        if not self.can_trade():
            logger.warning("Trade cooldown active, skipping buy.")
            return False

        if not self.check_trade_limits(user_id, amount_sol):
            logger.warning(f"Trade rejected by limit check for user {user_id}.")
            return False

        try:
            logger.info(f"Executing buy: {amount_sol} SOL -> {token_symbol} for user {user_id}")
            success = self.wallet.swap_token(token_symbol, amount_sol)
            if success:
                self.last_trade_time = time.time()
                log_trade(user_id, "buy", token_symbol, amount_sol)
                logger.info(f"Buy executed: {amount_sol} SOL -> {token_symbol}")
            else:
                logger.error("Buy transaction failed.")
            return success
        except Exception as e:
            logger.error(f"Error executing buy: {e}")
            return False

    def execute_sell(self, token_symbol: str, amount_tokens: float, user_id: Optional[int] = None, max_slippage_bps=50) -> bool:
        """Execute sell order for a token with checks and logging."""
        if not self.can_trade():
            logger.warning("Trade cooldown active, skipping sell.")
            return False

        # Placeholder: Implement token->SOL swap logic here.
        # For now, just log and return False to indicate not implemented.
        logger.warning("Sell execution not implemented yet.")
        return False

    def trigger_trade_on_alert(self, alert_type: str, token_symbol: str, amount_sol: float, user_id: Optional[int] = None):
        """
        Example method to trigger trades based on alerts (price targets, sentiment, etc).

        alert_type can be "price_target_hit", "sentiment_bullish", etc.
        Customize the logic per your strategy.
        """
        logger.info(f"Alert received: {alert_type} for {token_symbol}, amount {amount_sol} SOL")
        # Simple example: auto-buy if price target hit and trade allowed
        if alert_type == "price_target_hit":
            self.execute_buy(token_symbol, amount_sol, user_id=user_id)

        # You can extend for other alert types and trade logic here
