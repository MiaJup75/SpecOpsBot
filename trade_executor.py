import logging
from wallet import Wallet
from time import time

logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, wallet: Wallet, cooldown_seconds=60):
        self.wallet = wallet
        self.last_trade_time = 0
        self.cooldown_seconds = cooldown_seconds  # Prevent too frequent trades

    def can_trade(self) -> bool:
        """Check if cooldown period passed for next trade."""
        return (time() - self.last_trade_time) > self.cooldown_seconds

    def execute_buy(self, token_symbol: str, amount_sol: float, max_slippage_bps=50) -> bool:
        """Execute buy order for a given token."""
        if not self.can_trade():
            logger.warning("Trade cooldown active, skipping buy.")
            return False

        try:
            logger.info(f"Attempting to buy {amount_sol} SOL worth of {token_symbol} with max slippage {max_slippage_bps}bps")
            success = self.wallet.swap_token(token_symbol, amount_sol)
            if success:
                self.last_trade_time = time()
                logger.info(f"Buy order successful: {token_symbol}")
            else:
                logger.error(f"Buy order failed for {token_symbol}")
            return success
        except Exception as e:
            logger.error(f"Exception during buy execution: {e}")
            return False

    def execute_sell(self, token_symbol: str, amount_tokens: float, max_slippage_bps=50) -> bool:
        """
        Execute sell order.
        Currently placeholder — needs implementation based on wallet and dex capabilities.
        """
        logger.warning("Sell execution not implemented yet.")
        # TODO: Implement sell logic similar to buy, possibly swapping token back to SOL or USDC
        return False
