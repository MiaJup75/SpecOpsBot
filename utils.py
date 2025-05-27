
import requests
from config import config

def is_allowed(user_id):
    return str(user_id) in config["whitelist"]

def fetch_max_token_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    response = requests.get(url)
    data = response.json()["pair"]

    price = data["priceUsd"]
    market_cap = data["marketCap"]
    liquidity = data["liquidity"]["usd"]
    txns = data["txns"]["h24"]
    holders = "N/A"  # Dexscreener doesn't provide holders directly
    price_change = data["priceChange"]["h24"]
    created_timestamp = data["pairCreatedAt"]

    message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${float(price):,.8f}
📈 Price Change (24h): {price_change}%
🏛️ Market Cap: ${int(market_cap):,}
💧 Liquidity: ${int(liquidity):,}
🧾 24H TXNs: {txns['buys']} buys / {txns['sells']} sells
⏳ Launch Age: {created_timestamp}
📊 Holders: {holders}
🔗 <a href='https://dexscreener.com/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc'>View on Dexscreener</a>
"""

    return message

def get_trending_coins():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    response = requests.get(url)
    data = response.json().get("pairs", [])[:5]

    coins = []
    for i, coin in enumerate(data, start=1):
        name = coin["baseToken"]["symbol"]
        price = coin["priceUsd"]
        volume = coin["volume"]["h24"]
        coins.append(f"{i}. {name} – ${float(price):,.8f} – Vol: ${int(volume):,}")

    message = "🚀 <b>Trending Solana Meme Coins</b>
" + "\n".join(coins)
    return message
