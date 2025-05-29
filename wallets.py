# wallets.py – Wallet Watch Commands & Summary

from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from db import add_wallet, get_wallets

def handle_watch_command(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Usage: /watch <wallet_address> [nickname]")
        return

    address = context.args[0]
    label = " ".join(context.args[1:]) if len(context.args) > 1 else f"Wallet {address[:4]}...{address[-4:]}"
    
    try:
        add_wallet(label, address)
        update.message.reply_text(
            f"✅ Watching wallet:\n<code>{address}</code>\nNickname: {label}",
            parse_mode=ParseMode.HTML
        )
    except Exception:
        update.message.reply_text("⚠️ Error adding wallet.")

def handle_wallets_command(update: Update, context: CallbackContext, via_callback=False):
    wallets = get_wallets()
    if not wallets:
        msg = "No wallets are currently being tracked."
    else:
        msg = "<b>👛 Watched Wallets</b>\n" + "\n".join(
            [f"• {label}\n<code>{addr}</code>" for label, addr in wallets]
        )
    if via_callback:
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def get_wallet_summary():
    wallets = get_wallets()
    if not wallets:
        return "No wallets are currently being tracked."
    
    return "<b>👛 Watched Wallets</b>\n" + "\n".join(
        [f"• {label}\n<code>{addr}</code>" for label, addr in wallets]
    )
