from db import add_token, get_tokens, remove_token
from token_config import get_token_config

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

    # Build clickable inline keyboard with tokens
    buttons = []
    for token in tokens:
        buttons.append([InlineKeyboardButton(f"${token}", callback_data=f"token_{token}")])

    # Send list with buttons
    update.message.reply_text(
        "<b>📋 Tracked Tokens</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )

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
