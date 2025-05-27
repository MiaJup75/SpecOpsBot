import requests
from config import config
from datetime import datetime

def is_allowed(user_id):
    return str(user_id) in config["whitelist"]

def fetch_max_token_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
    try:
        response = requests.get(url)
        data = response.json().get("pair", {})

        price = data.get("priceUsd")
        market_cap = data.get("marketCap")
        volume = data.get("volume", {}).get("h24")
        fdv = data.get("fdv")
        buys = data.get("txns", {}).get("h24", {}).get("buys")
        sells = data.get("txns", {}).get("h24", {}).get("sells")
        liquidity = data.get("liquidity", {}).get("usd")
        change = data.get("priceChange", {}).get("h24")
        timestamp = data.get("pairCreatedAt")

        launch_time = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M UTC')

        message = f"""
🐶 <b>MAX Token Update</b>
💰 Price: ${price}
🏛️ Market Cap: ${int(market_cap):,}
📉 Volume (24h): ${float(volume):,.2f}
🏦 FDV: ${int(fdv):,}
📊 Buys: {buys} | Sells: {sells}
💧 Liquidity: ${float(liquidity):,.2f}
📈 24H Change: {change}%
🕐 Launch Time: {launch_time}
🔗 <a href="https://dexscreener.com/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc">View on Dexscreener</a>
        """.strip()
        return message
    except Exception as e:
        return f"⚠️ Failed to fetch MAX token data.\n{e}"

def get_trending_coins():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url)
        pairs = response.json().get("pairs", [])[:5]

        message = "<b>🚀 Trending Solana Meme Coins</b>\n"
        for i, pair in enumerate(pairs, 1):
            symbol = pair.get("baseToken", {}).get("symbol", "N/A")
            price = pair.get("priceUsd", "N/A")
            volume = pair.get("volume", {}).get("h24", 0)
            message += f"{i}. {symbol} – ${price} – Vol: ${volume:,.0f}\n"
        return message
    except Exception as e:
        return f"⚠️ Failed to fetch trending coins.\n{e}"

def fetch_new_tokens(stealth_only=False):
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url)
        pairs = response.json().get("pairs", [])
        results = []

        for pair in pairs:
            if not pair.get("pairCreatedAt"):
                continue
            created = datetime.utcfromtimestamp(pair["pairCreatedAt"] / 1000)
            age_minutes = (datetime.utcnow() - created).total_seconds() / 60
            if age_minutes > 720:  # older than 12h
                continue
            if stealth_only:
                socials = pair.get("info", {}).get("socials", [])
                if socials:
                    continue
            symbol = pair.get("baseToken", {}).get("symbol", "N/A")
            price = pair.get("priceUsd", "N/A")
            volume = pair.get("volume", {}).get("h24", 0)
            results.append(f"🔸 {symbol} – ${price} – Vol: ${volume:,.0f}")

        if not results:
            return "🕵️ No new tokens found." if not stealth_only else "👻 No stealth launches found."
        title = "🆕 <b>New Tokens</b>\n" if not stealth_only else "👻 <b>Stealth Radar</b>\n"
        return title + "\n".join(results)
    except Exception as e:
        return f"⚠️ Failed to fetch new token data.\n{e}"

def check_suspicious_activity():
    # Placeholder
    return "🚨 Suspicious activity scanning not yet implemented."

def fetch_wallet_activity():
    # Placeholder
    return "👛 Wallet monitoring results not available yet."

def fetch_sentiment_score():
    # Placeholder score generator
    score = "🔥 Meme Sentiment Score: 82/100\n🙂 Positive sentiment dominating Twitter and Telegram."
    return f"<b>📈 Sentiment Engine</b>\n{score}"

def track_position():
    # Placeholder PnL logic
    return "<b>📊 Position Tracker</b>\n• Entry: $0.00028\n• Current: $0.00033\n• ROI: +17.8%"

def send_target_alerts():
    return "<b>🎯 Target Alerts</b>\nMAX Token has <u>not</u> crossed your sell threshold yet."

def fetch_token_classification(daily=False):
    # Placeholder narrative classifier
    trends = [
        "🐸 Frog-themed coins still leading",
        "🧠 AI/Meme hybrid narrative gaining momentum",
        "💎 Liquidity-focused plays emerging"
    ]
    if daily:
        msg = "<b>📊 Daily Narrative Summary</b>\n"
    else:
        msg = "<b>🧠 Narrative Classifier</b>\n"
    msg += "\n".join(f"• {trend}" for trend in trends)
    return msg
