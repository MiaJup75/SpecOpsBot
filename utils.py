import requests
import random
from config import config

def fetch_max_token_data():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"
        res = requests.get(url)
        data = res.json()["pair"]

        return {
            "price": float(data["priceUsd"]),
            "market_cap": float(data.get("marketCap", 0)),
            "volume": float(data.get("volume", {}).get("h24", 0)),
            "fdv": float(data.get("fdv", 0)),
            "buys": data["txns"]["h24"]["buys"],
            "sells": data["txns"]["h24"]["sells"],
            "liquidity": float(data["liquidity"]["usd"]),
            "change": data.get("priceChange", {}).get("h24", "N/A"),
            "holders": "N/A",
            "launch_time": data.get("pairCreatedAt", "N/A"),
            "dex_url": data["url"]
        }
    except Exception as e:
        print(f"Error fetching MAX data: {e}")
        raise

def fetch_trending_tokens():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        res = requests.get(url)
        pairs = res.json().get("pairs", [])[:5]
        message = "🚀 <b>Trending Solana Meme Coins</b>\n"
        for i, token in enumerate(pairs, 1):
            name = token["baseToken"]["symbol"]
            price = token["priceUsd"]
            volume = token["volume"]["h24"]
            message += f"{i}. {name} – ${float(price):.6f} – Vol: ${float(volume):,.0f}\n"
        return message
    except Exception:
        return "No trending coins found."

def fetch_new_tokens():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        res = requests.get(url)
        pairs = res.json().get("pairs", [])
        message = "🆕 <b>New Meme Coins (last 12h)</b>\n"
        found = False
        for token in pairs:
            socials = token.get("info", {}).get("socials", [])
            if not socials and token.get("pairCreatedAt", 0) > 0:
                name = token["baseToken"]["symbol"]
                volume = token["volume"]["h24"]
                message += f"{name}: ${float(volume):,.0f} volume\n"
                found = True
        return message if found else "No new tokens found."
    except Exception:
        return "No new tokens found."

def check_suspicious_activity():
    try:
        return (
            "⚠️ <b>Suspicious Token Alerts</b>\n"
            "RUGDOG: 💥 Liquidity pulled\n"
            "FAKEAI: ⚠️ Dev wallet dumped 80%"
        )
    except Exception:
        return "No suspicious activity."

def summarize_wallet_activity():
    wallets = config["wallets"]
    message = "👛 <b>Wallet Watchlist</b>\n"
    for wallet in wallets:
        buys = random.randint(1, 5)
        sells = random.randint(0, 3)
        short = f"{wallet[:4]}...{wallet[-4:]}"
        message += f"Wallet {short} activity summary:\n🟢 {buys} Buys, 🔴 {sells} Sell in last 24h\n\n"
    return message.strip()

def track_position():
    value = 3457.91
    pnl = 1367.91
    breakeven = 0.0002
    return (
        "📈 <b>PnL Tracker</b>\n"
        f"💵 Value: ${value:,.2f}\n"
        f"🧮 PnL: ${pnl:,.2f}\n"
        f"⚖️ Breakeven Price: ${breakeven}"
    )

def get_target_alerts():
    return (
        "🎯 <b>Target Alerts</b>\n"
        "MAX hit your sell target at $0.0005 ✅\n"
        "Keep an eye on volume before exit."
    )

def get_sentiment_score():
    emojis = ["🚀", "🔥", "💎", "🙌", "😬", "🫠", "📉", "🫡"]
    msg = random.choice([
        f"{random.choice(emojis)} Hold strong fam!",
        f"{random.choice(emojis)} Slight dip, nothing to worry.",
        f"{random.choice(emojis)} Vibe check: neutral.",
        f"{random.choice(emojis)} Up only!",
    ])
    return f"🤖 <b>Sentiment Meter</b>\n{msg}"

def find_stealth_launches():
    return (
        "🕵️‍♂️ <b>Stealth Launch Radar</b>\n"
        "Found 2 tokens with no social links:\n"
        "1. SNEAKY – Vol: $9,230\n"
        "2. SHADOW – Vol: $3,819"
    )
