import requests
from datetime import datetime
from config import config


def is_allowed(user_id):
    return str(user_id) in config["whitelist"]


def fetch_max_token_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("pair", {})
        return {
            "priceUsd": data.get("priceUsd"),
            "marketCap": data.get("marketCap"),
            "fdv": data.get("fdv"),
            "volume": data.get("volume", {}).get("h24")
        }
    return None


def format_max_message(data):
    if not data:
        return "❌ Unable to fetch MAX token data."

    return f"""
🐶 <b>MAX Token Update</b>
💰 <b>Price:</b> ${float(data['priceUsd']):,.8f}
🏛️ <b>Market Cap:</b> ${int(data['marketCap']):,}
📉 <b>Volume (24h):</b> ${int(data['volume']):,}
🏦 <b>FDV:</b> ${int(data['fdv']):,}
"""


def fetch_trending_coins():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    all_pairs = response.json().get("pairs", [])
    filtered = [
        pair for pair in all_pairs
        if pair["baseToken"]["symbol"] != "SOL"
        and float(pair["liquidity"]["usd"]) > 10000
    ]
    sorted_pairs = sorted(filtered, key=lambda x: float(x["volume"]["h24"]), reverse=True)
    return sorted_pairs[:5]


def format_trending_coins(coins):
    if not coins:
        return "❌ Unable to fetch trending coins."

    message = "<b>🚀 Trending Solana Meme Coins</b>\n"
    for i, coin in enumerate(coins, 1):
        symbol = coin["baseToken"]["symbol"]
        price = float(coin["priceUsd"])
        volume = float(coin["volume"]["h24"])
        message += f"{i}. <b>{symbol}</b> – ${price:,.8f} – Vol: ${int(volume):,}\n"
    return message


def fetch_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    all_pairs = response.json().get("pairs", [])
    threshold_time = int((datetime.utcnow().timestamp() - 86400) * 1000)

    return [
        {
            "symbol": p["baseToken"]["symbol"],
            "created": datetime.utcfromtimestamp(p["pairCreatedAt"] / 1000).strftime('%Y-%m-%d %H:%M'),
            "url": p["url"]
        }
        for p in all_pairs
        if p.get("pairCreatedAt", 0) > threshold_time and float(p["liquidity"]["usd"]) > 10000
    ]


def format_new_tokens(tokens):
    if not tokens:
        return "🤖 No new meme coins launched in the past 24h."

    message = "<b>🆕 New Token Watch (24h)</b>\n"
    for t in tokens[:5]:
        message += f"• <b>{t['symbol']}</b> – Launched: {t['created']}\n🔗 {t['url']}\n"
    return message


def check_suspicious_activity():
    # Dummy output for now
    return """
⚠️ <b>Suspicious Activity Monitor</b>
• Dev wallet 3xu... pulled 75% of LP on 🐸 PEPE2
• Whale sold 900k tokens from MAX in a single txn
• Botnet detected spamming $FOMO buys
"""


def track_position():
    return """
📈 PnL Tracker:
Break-even: $0.00032
Current: $0.00034
PnL: +6.25%
"""
