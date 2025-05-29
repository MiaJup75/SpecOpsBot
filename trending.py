# trending.py – Trending Tokens Handler

import requests
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/pairs/solana"

def fetch_trending_tokens(limit=10):
    try:
        response = requests.get(DEXSCREENER_API)
        response.raise_for_status()
        data = response.json()
        pairs = data.get("pairs", [])[:limit]

        trending = []
        for pair in pairs:
            name = pair.get("baseToken", {}).get("name", "")
            symbol = pair.get("baseToken", {}).get("symbol", "")
            price = pair.get("priceUsd", "N/A")
            market_cap = pair.get("fdv", "N/A")
            volume = pair.get("volume", {}).get("h24", "N/A")
            link = pair.get("url", "")
            trending.append({
                "name": name,
                "symbol": symbol,
                "price": price,
                "market_cap": market_cap,
                "volume": volume,
                "link": link
            })
        return trending
    except Exception as e:
        print(f"Error fetching trending tokens: {e}")
        return []

def handle_trending_command(update: Update, context: CallbackContext):
    trending = fetch_trending_tokens()
    if not trending:
        update.message.reply_text("⚠️ Could not fetch trending tokens.")
        return

    msg = "<b>🔥 Top Trending Solana Tokens</b>\n"
    buttons = []

    for token in trending:
        msg += f"\n<b>{token['symbol']}</b> – ${float(token['price']):.4f}\n"
        msg += f"💰 MCap: ${int(token['market_cap']):,} | 📊 Vol: ${int(token['volume']):,}\n"
        msg += f"<a href='{token['link']}'>🔗 Dexscreener</a>\n"
        msg += "—" * 15 + "\n"

        buttons.append([InlineKeyboardButton(f"{token['symbol']}", url=token['link'])])

    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
