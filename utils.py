import requests
import json

with open("config.json", "r") as f:
    config = json.load(f)

def is_allowed(user_id):
    return str(user_id) in config["whitelist"]

def fetch_max_token_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    response = requests.get(url)
    data = response.json()["pair"]
    return float(data["priceUsd"]), int(float(data["marketCap"])), int(float(data["volume"]["h24"])), int(float(data["fdv"]))

def get_trending_coins():
    url = "https://api.dexscreener.com/latest/dex/search/?q=solana"
    response = requests.get(url)
    data = response.json()
    coins = []
    for pair in data.get("pairs", [])[:5]:
        coins.append({
            "symbol": pair["baseToken"]["symbol"],
            "priceUsd": float(pair["priceUsd"]),
            "volume": int(float(pair["volume"]["h24"]))
        })
    return coins