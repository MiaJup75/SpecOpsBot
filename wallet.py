import os
import base64
import logging
import requests
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed

RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

class Wallet:
    def __init__(self):
        b64_key = os.getenv("BURNER_SECRET_KEY_B64")
        if not b64_key:
            raise Exception("BURNER_SECRET_KEY_B64 not set")
        key_bytes = base64.b64decode(b64_key)
        self.keypair = Keypair.from_secret_key(key_bytes)
        self.client = Client(RPC_URL)
        self.logger = logging.getLogger(__name__)

    def buy_token(self, symbol: str, amount: float) -> str:
        TOKEN_OVERRIDES = {
            "MAX": {
                "mint": "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump",
            },
            # Add your other tokens here
        }

        if symbol not in TOKEN_OVERRIDES:
            return f"⚠️ Token symbol {symbol} not recognized."

        try:
            mint = TOKEN_OVERRIDES[symbol]["mint"]
            # Convert SOL amount to lamports
            amount_lamports = int(amount * 1_000_000_000)

            url = (
                "https://quote-api.jup.ag/v1/quote?"
                f"inputMint=So11111111111111111111111111111111111111112&"
                f"outputMint={mint}&"
                f"amount={amount_lamports}&"
                f"slippage=1"
            )
            self.logger.info(f"Requesting Jupiter quote: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return f"⚠️ Jupiter API error: HTTP {response.status_code}"

            data = response.json()
            if not data.get("data"):
                return "⚠️ No swap routes found by Jupiter."

            route = data["data"][0]
            swap_tx_base64 = route["swapTransaction"]

            tx_bytes = base64.b64decode(swap_tx_base64)
            transaction = Transaction.deserialize(tx_bytes)
            transaction.sign(self.keypair)

            tx_sig = self.client.send_raw_transaction(transaction.serialize(), opts=TxOpts(skip_confirmation=False))

            self.client.confirm_transaction(tx_sig["result"], commitment=Confirmed)

            return f"✅ Bought {amount} {symbol}. Tx signature: {tx_sig['result']}"

        except Exception as e:
            self.logger.error(f"Error during buy_token: {e}")
            return f"⚠️ Swap failed: {e}"
