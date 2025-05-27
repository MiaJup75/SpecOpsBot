import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
BURNER_SECRET_KEY_B64 = os.getenv("BURNER_SECRET_KEY_B64")

def validate_config():
    missing = [k for k in ["BOT_TOKEN", "CHAT_ID"] if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing required env variables: {', '.join(missing)}")
