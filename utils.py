# utils.py
import requests, json

def fetch_max_token_data():
    url = "https://multichain-api.birdeye.so/solana/overview/token_stats?address=EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump&time_frame=24h"
    headers = {"accept": "application/json"}
    r = requests.get(url, headers=headers).json()
    return {
        "price": round(r["data"]["price"], 6),
        "market_cap": int(r["data"]["market_cap"]),
        "liquidity": int(r["data"]["liquidity"]["usd"]),
        "volume": int(r["data"]["volume"]["value"]),
        "fdv": int(r["data"]["fdv"])
    }

def is_allowed(user_id):
    with open("config.json", "r") as f:
        return str(user_id) in json.load(f)["whitelist"]
