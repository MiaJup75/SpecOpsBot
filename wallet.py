import base64
import logging
import os
import requests
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.system_program import SYS_PROGRAM_ID
from solana.rpc.commitment import Confirmed
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.core import RPCException

logger = logging.getLogger(__name__)

JUPITER_QUOTE_API = "https://quote-api.jup.ag/v1/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v1/swap"

class Wallet:
    def __init__(self):
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.client = Client(self.rpc_url)
        b64_key = os.getenv("BURNER_SECRET_KEY_B64")
        if not b64_key:
            raise Exception("BURNER_SECRET_KEY_B64 environment variable not set")

        try:
            key_bytes = base64.b64decode(b64_key)
            self.keypair = Keypair.from_secret_key(key_bytes)
        except Exception as e:
            logger.error(f"Error decoding BURNER_SECRET_KEY_B64: {e}")
            raise

    def get_token_mint(self, symbol: str) -> str:
        # Minimal example: extend with real mint data or API call
        token_mints = {
            "SOL": "So11111111111111111111111111111111111111112",
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            # Add more token mints here
        }
        return token_mints.get(symbol.upper(), "")

    def swap_token(self, token_symbol: str, amount: float) -> bool:
        try:
            logger.info(f"Preparing to swap {amount} SOL to {token_symbol}")
            output_mint = self.get_token_mint(token_symbol)
            if not output_mint:
                logger.error(f"Unknown token symbol or mint not configured: {token_symbol}")
                return False

            # Step 1: Get quote from Jupiter API
            params = {
                "inputMint": "So11111111111111111111111111111111111111112",  # SOL mint
                "outputMint": output_mint,
                "amount": int(amount * 1e9),  # amount in lamports (1 SOL = 1e9 lamports)
                "slippageBps": 50,  # 0.5% slippage tolerance
                "onlyDirectRoutes": True
            }
            resp = requests.get(JUPITER_QUOTE_API, params=params)
            resp.raise_for_status()
            data = resp.json()
            routes = data.get("data", [])

            if not routes:
                logger.error("No swap routes found from Jupiter API")
                return False

            best_route = routes[0]  # Pick the best route (lowest price impact)
            logger.info(f"Selected route: {best_route}")

            # Step 2: Get swap transaction data from Jupiter API
            swap_params = {
                "route": best_route,
                "userPublicKey": str(self.keypair.public_key)
            }
            swap_resp = requests.post(JUPITER_SWAP_API, json=swap_params)
            swap_resp.raise_for_status()
            swap_tx_data = swap_resp.json()

            if "swapTransaction" not in swap_tx_data:
                logger.error("No swapTransaction data in Jupiter API response")
                return False

            tx_bytes_base64 = swap_tx_data["swapTransaction"]
            tx_bytes = base64.b64decode(tx_bytes_base64)

            # Step 3: Deserialize transaction and sign it
            from solana.transaction import Transaction
            from solana.rpc.api import Client
            from solana.rpc.commitment import Confirmed

            transaction = Transaction.deserialize(tx_bytes)
            transaction.sign(self.keypair)

            # Step 4: Send transaction
            resp = self.client.send_transaction(transaction, self.keypair, opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed))
            logger.info(f"Transaction sent: {resp}")

            if not resp.get("result"):
                logger.error(f"Transaction failed or no result: {resp}")
                return False

            logger.info(f"Swap transaction signature: {resp['result']}")
            return True

        except requests.HTTPError as e:
            logger.error(f"HTTP error during swap: {e}")
            return False
        except RPCException as e:
            logger.error(f"RPC error during swap: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during swap: {e}")
            return False
