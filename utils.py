
import json
import requests

with open("config.json") as f:
    config = json.load(f)

def is_allowed(update):
    user_id = str(update.effective_user.id)
    return user_id in config["whitelist"]

def fetch_max_token_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    try:
        response = requests.get(url)
        data = response.json()["pair"]
        price = data["priceUsd"]
        market_cap = data["marketCap"]
        volume = data["volume"]["h24"]
        fdv = data["fdv"]
        txns = data["txns"]["h24"]
        holders = "N/A"
        liquidity = data["liquidity"]["usd"]
        price_change = data["priceChange"]["h24"]
        launch_age = data["pairCreatedAt"]

        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${price}
🏛️ Market Cap: ${market_cap}
📉 Volume (24h): ${volume}
🏦 FDV: ${fdv}
🔁 24H TXNs: Buys {txns['buys']} / Sells {txns['sells']}
👥 Holders: {holders}
💧 Liquidity: ${liquidity}
📈 24H Price Change: {price_change}%
⏱️ Launch Time: {launch_age}
🔗 <a href='https://dexscreener.com/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc'>Dexscreener Link</a>"""
        return message
    except Exception as e:
        return f"⚠️ Error fetching MAX token data: {e}"
