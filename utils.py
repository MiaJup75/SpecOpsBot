
import requests
from config import config

def is_allowed(user_id):
    return str(user_id) in config["whitelist"]

def fetch_max_token_data():
    response = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc")
    data = response.json()["pairs"][0]

    buys = data["txns"]["h24"]["buys"]
    sells = data["txns"]["h24"]["sells"]
    holders = "N/A"
    liquidity = round(data["liquidity"]["usd"], 2)
    price_change = data["priceChange"]["h24"]
    market_cap = round(data["marketCap"], 2)
    price = data["priceUsd"]
    fdv = data["fdv"]
    volume = round(data["volume"]["h24"], 2)
    launched_at = data.get("pairCreatedAt", "N/A")

    return {
        "price": price,
        "market_cap": market_cap,
        "volume": volume,
        "fdv": fdv,
        "buys": buys,
        "sells": sells,
        "holders": holders,
        "liquidity": liquidity,
        "price_change": price_change,
        "launched_at": launched_at,
    }

def get_trending_coins():
    coins = [
        {"name": "DOGGO", "price": "$0.0009", "volume": "$12,345"},
        {"name": "MEOW", "price": "$0.0012", "volume": "$8,901"},
        {"name": "ZAP", "price": "$0.045", "volume": "$22,000"},
        {"name": "RAWR", "price": "$0.00005", "volume": "$3,210"},
        {"name": "BLOOP", "price": "$0.75", "volume": "$18,450"},
    ]

    message = (
        "🚀 <b>Trending Solana Meme Coins</b>\n"
        + "\n".join([f"{i+1}. {coin['name']} – {coin['price']} – Vol: {coin['volume']}" for i, coin in enumerate(coins)])
    )
    return message
