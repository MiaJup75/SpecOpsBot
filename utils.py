
import json
import requests

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
WHITELIST = config.get("whitelist", [])
MAX_TOKEN_ADDRESS = config.get("max_token")
BIRDEYE_API_URL = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN_ADDRESS}&time_frame=24h"

def is_allowed(user_id):
    return str(user_id) in WHITELIST

def fetch_max_token_data():
    try:
        response = requests.get(BIRDEYE_API_URL)
        response.raise_for_status()
        data = response.json().get("data", {})
        return {
            "price": data.get("price", 0),
            "market_cap": data.get("market_cap", 0),
            "volume": data.get("volume_24h_quote", 0),
            "fdv": data.get("fdv", 0),
            "liquidity": data.get("liquidity", 0)
        }
    except Exception as e:
        print(f"Error fetching token data: {e}")
        return {}
