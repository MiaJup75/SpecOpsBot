import requests
from config import config
from telegram import ParseMode
from datetime import datetime

def fetch_max_token_data(chat_id):
    try:
        token_address = config["max_token"]
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{token_address}"
        res = requests.get(url).json()

        pair_data = res.get("pair", {})
        if not pair_data:
            raise Exception("No data")

        price = float(pair_data.get("priceUsd", 0))
        mc = int(pair_data.get("marketCap", 0))
        volume = float(pair_data["volume"]["h24"])
        fdv = int(pair_data.get("fdv", 0))
        liquidity = float(pair_data["liquidity"]["usd"])
        buys = pair_data["txns"]["h24"]["buys"]
        sells = pair_data["txns"]["h24"]["sells"]
        change = pair_data["priceChange"]["h24"]
        link = pair_data.get("url", "https://dexscreener.com")

        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${price:.8f}
🏛️ Market Cap: ${mc:,}
📉 Volume (24h): ${volume:,.2f}
🏦 FDV: ${fdv:,}
📊 Buys: {buys} | Sells: {sells}
💧 Liquidity: ${liquidity:,.2f}
📈 24H Change: {change:.2f}%
🔗 <a href="{link}">View on Dexscreener</a>"""

        from main import bot
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        from main import bot
        bot.send_message(chat_id=chat_id, text="❌ Unable to fetch MAX token data.", parse_mode=ParseMode.HTML)

def get_trending_coins(chat_id):
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        res = requests.get(url).json()

        top = sorted(res["pairs"], key=lambda x: x["volume"]["h24"], reverse=True)[:5]
        message = "🚀 <b>Trending Solana Meme Coins</b>\n"
        for i, pair in enumerate(top, 1):
            name = pair["baseToken"]["symbol"]
            price = float(pair.get("priceUsd", 0))
            vol = float(pair["volume"]["h24"])
            message += f"{i}. {name} – ${price:.8f} – Vol: ${vol:,.0f}\n"

        from main import bot
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
    except Exception:
        from main import bot
        bot.send_message(chat_id=chat_id, text="❌ Unable to fetch trending coins.", parse_mode=ParseMode.HTML)

def fetch_new_tokens(chat_id):
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        res = requests.get(url).json()
        now = datetime.utcnow().timestamp()

        new_tokens = [pair for pair in res["pairs"] if (now - (pair["pairCreatedAt"] / 1000)) <= 43200]
        message = "🆕 <b>New Token Watch (<12h old)</b>\n"

        if not new_tokens:
            message += "No new tokens detected."
        else:
            for p in new_tokens[:5]:
                name = p["baseToken"]["symbol"]
                vol = p["volume"]["h24"]
                locked = "Yes" if p["liquidity"]["usd"] > 10000 else "Low"
                message += f"• {name} – Vol: ${vol:,.0f} – LP Locked: {locked}\n"

        from main import bot
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
    except Exception:
        from main import bot
        bot.send_message(chat_id=chat_id, text="❌ Failed to fetch new token data.", parse_mode=ParseMode.HTML)

def check_suspicious_activity(chat_id):
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        res = requests.get(url).json()
        flagged = []
        for p in res["pairs"]:
            if p["liquidity"]["usd"] < 5000 or abs(p["priceChange"]["h1"]) > 50:
                flagged.append(p)

        message = "⚠️ <b>Suspicious Activity Alerts</b>\n"
        if not flagged:
            message += "No major alerts in the last hour."
        else:
            for p in flagged[:5]:
                name = p["baseToken"]["symbol"]
                change = p["priceChange"]["h1"]
                vol = p["volume"]["h1"]
                message += f"• {name} – {change:.1f}% – Vol: ${vol:,.0f}\n"

        from main import bot
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
    except Exception:
        from main import bot
        bot.send_message(chat_id=chat_id, text="❌ Could not check suspicious activity.", parse_mode=ParseMode.HTML)

def summarize_wallet_activity(chat_id):
    try:
        wallets = config["wallets"]
        message = "👛 <b>Wallet Tracker</b>\n"
        if not wallets:
            message += "No tracked wallets."
        else:
            for addr in wallets:
                message += f"• {addr[:6]}...{addr[-4:]} – Watching\n"

        from main import bot
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
    except Exception:
        from main import bot
        bot.send_message(chat_id=chat_id, text="❌ Error loading wallets.", parse_mode=ParseMode.HTML)

# Placeholder Tier 3 features
def track_position(chat_id):
    from main import bot
    bot.send_message(chat_id=chat_id, text="🧮 <b>PnL Tracking coming soon!</b>", parse_mode=ParseMode.HTML)

def send_target_alerts(chat_id):
    from main import bot
    bot.send_message(chat_id=chat_id, text="🎯 <b>Target alerts loading...</b>", parse_mode=ParseMode.HTML)
