from db import add_token, get_tokens, remove_token

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
