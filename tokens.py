import requests
from db import add_token, get_tokens, remove_token

def fetch_token_info(symbol: str) -> dict | None:
    token_map = {
        "MAX": {"pair": "8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc"},
        "LOOT": {"pair": "examplepairaddress1"},
        "ZOOM": {"pair": "examplepairaddress2"},
        "RUGME": {"pair": "examplepairaddress3"},
        # Add your other tokens here with their pair addresses
    }
    info = token_map.get(symbol.upper())
    if not info:
        return None
    pair = info["pair"]

    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair}"
    try:
        response = requests.get(url, timeout=5).json()
        pair_data = response.get("pair", {})
        return {
            "price": pair_data.get("priceUsd"),
            "market_cap": pair_data.get("marketCapUsd"),
            "liquidity": pair_data.get("liquidityUsd"),
            "pair": pair,
        }
    except Exception as e:
        print(f"[tokens.py] Error fetching token info for {symbol}: {e}")
        return None

def handle_add_token(update, context):
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /addtoken $TOKEN")
            return
        symbol = context.args[0].lstrip("$").upper()
        add_token(symbol)
        update.message.reply_text(f"✅ Token added to watchlist: ${symbol}")
    except Exception:
        update.message.reply_text("⚠️ Error adding token.")

def handle_tokens(update, context):
    tokens = get_tokens()
    if not tokens:
        update.message.reply_text("No tokens are currently being tracked.")
        return
    msg = "<b>📋 Tracked Tokens</b>\n" + "\n".join([f"• ${t}" for t in tokens])
    update.message.reply_text(msg, parse_mode="HTML")

def handle_remove_token(update, context):
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /removetoken $TOKEN")
            return
        symbol = context.args[0].lstrip("$").upper()
        remove_token(symbol)
        update.message.reply_text(f"🗑 Removed: ${symbol} from watchlist")
    except Exception:
        update.message.reply_text("⚠️ Could not remove token.")
