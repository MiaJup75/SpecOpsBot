# wallets.py – Command handlers for /wallets and /watch

from telegram import Update
from telegram.ext import CallbackContext
from wallet_db import add_wallet, get_wallets

def handle_watch_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        update.message.reply_text("Usage: /watch <wallet_address> [optional_label]")
        return

    address = context.args[0]
    label = " ".join(context.args[1:]) if len(context.args) > 1 else f"Wallet {address[:4]}...{address[-4:]}"
    
    try:
        add_wallet(label, address)
        update.message.reply_text(f"✅ Now watching wallet:\n<code>{address}</code>\nLabel: <b>{label}</b>",
                                  parse_mode="HTML")
    except Exception:
        update.message.reply_text("⚠️ Error adding wallet.")

def handle_wallets_command(update: Update, context: CallbackContext, via_callback=False) -> None:
    wallets = get_wallets()

    if not wallets:
        msg = "<b>👛 Watched Wallets</b>\n\nNo wallets are currently being tracked.\nUse /watch to add one."
    else:
        lines = [f"• <b>{label}</b>\n<code>{addr}</code>" for label, addr in wallets]
        msg = "<b>👛 Watched Wallets</b>\n\n" + "\n\n".join(lines)

    if via_callback:
        update.callback_query.edit_message_text(msg, parse_mode='HTML')
    else:
        update.message.reply_text(msg, parse_mode='HTML')
