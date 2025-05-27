import os
import logging
import requests
from base64 import b64decode
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

class Wallet:
    def __init__(self):
        b64_key = os.getenv("BURNER_SECRET_KEY_B64")
        if not b64_key:
            raise ValueError("BURNER_SECRET_KEY_B64 env var is missing")
        try:
            key_bytes = b64decode(b64_key)
            self.keypair = Keypair.from_secret_key(key_bytes)
        except Exception as e:
            logger.error(f"Error decoding BURNER_SECRET_KEY_B64: {e}")
            raise

        self.client = Client(SOLANA_RPC_URL)

    # Sample token overrides with mint addresses
    TOKEN_OVERRIDES = {
        "MAX": {
            "mint": "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump",
        },
        "BONK": {
            "mint": "So11111111111111111111111111111111111111112",  # Example; replace with actual
        },
        # Add more tokens here
    }

    def buy_token(self, symbol: str, amount_sol: float) -> str:
        symbol = symbol.upper()
        if symbol not in self.TOKEN_OVERRIDES:
            return f"❌ Token {symbol} not supported for buying."

        mint_address = self.TOKEN_OVERRIDES[symbol]["mint"]
        try:
            # For simplicity, simulate the swap call (replace with Jupiter swap integration)
            # In real: build transaction using Jupiter aggregator API, sign and send it
            logger.info(f"Attempting to buy {amount_sol} SOL worth of {symbol} (mint {mint_address})")

            # Check SOL balance
            balance_resp = self.client.get_balance(self.keypair.public_key)
            if balance_resp['result']['value'] < int(amount_sol * 1e9):
                return "❌ Insufficient SOL balance to perform swap."

            # Placeholder: this example just transfers SOL to self (replace with real swap tx)
            tx = Transaction()
            tx.add(
                transfer(
                    TransferParams(
                        from_pubkey=self.keypair.public_key,
                        to_pubkey=self.keypair.public_key,
                        lamports=int(amount_sol * 1e9),
                    )
                )
            )
            resp = self.client.send_transaction(tx, self.keypair)
            if resp.get('result'):
                tx_sig = resp['result']
                logger.info(f"Swap transaction sent: {tx_sig}")
                return f"✅ Swap transaction sent for {amount_sol} SOL of {symbol}. Tx: {tx_sig}"
            else:
                logger.error(f"Swap transaction failed: {resp}")
                return f"❌ Swap transaction failed: {resp}"
        except Exception as e:
            logger.error(f"Error executing swap: {e}")
            return f"❌ Error executing swap: {e}"
