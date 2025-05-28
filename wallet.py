import base64
import logging
import os
import requests
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.rpc.commitment import Confirmed
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
            self.keypair = Keypair.from_secret
