# tokens.py – Token Watch Commands & Utilities

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from db import add_token, get_tokens, remove_token

def handle_addtoken_command(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /addtoken $TOKEN")
        return

    symbol = context.args[0].lstrip("$")
    try:
        add_token(symbol)
        update.message.reply_text(f"✅ Watching token: ${symbol.upper()}")
    except Exception as e:
        update.message.reply_text("⚠️ Error adding token.")
        print(f"Error adding token: {e}")

def handle_tokens_command(update: Update, context: CallbackContext, via_callback=False):
    tokens = get_tokens()
    if not tokens:
        msg = "No tokens being watched."
    else:
        token_list = "\n".join([f"• ${t}" for t in tokens])
        msg = f"<b>📋 Watched Tokens</b>\n{token_list}"

    keyboard = [
        [InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat="/addtoken $")],
        [InlineKeyboardButton("🗑 Remove Token", switch_inline_query_current_chat="/removetoken $")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if via_callback:
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    else:
        update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

def handle_removetoken_command(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /removetoken $TOKEN")
        return

    symbol = context.args[0].lstrip("$")
    try:
        remove_token(symbol)
        update.message.reply_text(f"✅ Removed token: ${symbol.upper()}")
    except Exception as e:
        update.message.reply_text("⚠️ Error removing token.")
        print(f"Error removing token: {e}")

def get_tokens_list():
    tokens = get_tokens()
    if not tokens:
        return "No tokens being watched."

    return "<b>📋 Watched Tokens</b>\n" + "\n".join([f"• ${t}" for t in tokens])
