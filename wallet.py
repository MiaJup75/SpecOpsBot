import os
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from base64 import b64decode

SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

class Wallet:
    def __init__(self, secret_key_b64: str):
        secret_key_bytes = b64decode(secret_key_b64)
        self.keypair = Keypair.from_secret_key(secret_key_bytes)
        self.client = Client(SOLANA_RPC_URL)
        self.public_key = self.keypair.public_key

    def get_balance(self):
        resp = self.client.get_balance(self.public_key)
        return resp['result']['value'] / 1e9  # convert lamports to SOL

    def send_sol(self, to_pubkey: str, amount_sol: float):
        to_key = PublicKey(to_pubkey)
        lamports = int(amount_sol * 1e9)
        txn = Transaction()
        txn.add(
            transfer(
                TransferParams(
                    from_pubkey=self.public_key,
                    to_pubkey=to_key,
                    lamports=lamports
                )
            )
        )
        resp = self.client.send_transaction(txn, self.keypair)
        return resp
