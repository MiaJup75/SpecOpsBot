import os
import logging
import base64
import requests
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
JUPITER_API_URL = "https://quote-api.jup.ag/v1/quote"
JUPITER_SWAP_API_URL = "https://quote-api.jup.ag/v1/swap"

class Wallet:
    def __init__(self):
        b64_key = os.getenv("BURNER_SECRET_KEY_B64")
        if not b64_key:
            raise ValueError("BURNER_SECRET_KEY_B64 env var missing")
        try:
            key_bytes = base64.b64decode(b64_key)
            self.keypair = Keypair.from_secret_key(key_bytes)
        except Exception as e:
            logger.error(f"Error decoding BURNER_SECRET_KEY_B64: {e}")
            raise

        self.client = Client(SOLANA_RPC_URL)

    TOKEN_OVERRIDES = {
        "MAX": {
            "mint": "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump",
        },
        "BONK": {
            "mint": "BcNyZTcFGQK2R8ZzwTq6aJdFMSxTqudyA5qcGPPa1xRf",
        },
        "MEOW": {
            "mint": "4Q3zyzS2dVj3xxidqUTM8W6aTzv7wSLGxazqX9NR8kKz",
        },
        "CHAD": {
            "mint": "CHaD3DeDrzKJqVdzxh8jFqZBzUACaQhABqUeELyXmZtT",
        },
        "WEN": {
            "mint": "WENkDukxfYYkCXUfgPqX4pxhPqbaAX5cRpuqcMB8C7yA",
        },
        "SLERF": {
            "mint": "SLERFgXT7APNyiQF4gXvTQRcnP4aUZrZ39nFXxyWqGqw",
        }
    }

    def get_swap_route(self, input_mint: str, output_mint: str, amount: int):
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount),
            "slippageBps": 50,  # 0.5% slippage
            "onlyDirectRoutes": False
        }
        resp = requests.get(JUPITER_API_URL, params=params)
        if resp.status_code != 200:
            raise Exception(f"Jupiter API error: {resp.text}")
        data = resp.json()
        if not data.get("data"):
            raise Exception("No routes found by Jupiter")
        return data["data"][0]

    def execute_swap(self, route, user_public_key, user_keypair):
        swap_resp = requests.post(JUPITER_SWAP_API_URL, json={"route": route})
        if swap_resp.status_code != 200:
            raise Exception(f"Jupiter swap API error: {swap_resp.text}")

        swap_data = swap_resp.json()
        tx_data = swap_data["swapTransaction"]
        tx_bytes = base64.b64decode(tx_data)
        transaction = Transaction.deserialize(tx_bytes)
        transaction.sign(user_keypair)
        raw_tx = transaction.serialize()
        send_resp = self.client.send_raw_transaction(raw_tx, opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed))
        if "result" not in send_resp:
            raise Exception(f"Failed to send transaction: {send_resp}")
        return send_resp["result"]

    def buy_token(self, symbol: str, amount_sol: float) -> str:
        symbol = symbol.upper()
        if symbol not in self.TOKEN_OVERRIDES:
            return f"❌ Token {symbol} not supported."

        mint_address = self.TOKEN_OVERRIDES[symbol]["mint"]
        input_mint = "So11111111111111111111111111111111111111112"  # Wrapped SOL
        amount_lamports = int(amount_sol * 1_000_000_000)

        try:
            logger.info(f"Getting swap route for {amount_sol} SOL → {symbol}")
            route = self.get_swap_route(input_mint, mint_address, amount_lamports)
            logger.info("Route found, executing swap transaction")
            tx_sig = self.execute_swap(route, self.keypair.public_key, self.keypair)
            logger.info(f"Swap transaction sent: {tx_sig}")
            return f"✅ Swap executed for {amount_sol} SOL to {symbol}.\nTx Signature: {tx_sig}"
        except Exception as e:
            logger.error(f"Swap error: {e}")
            return f"❌ Swap failed: {e}"
