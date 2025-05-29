# wallets.py – Wallet Tracker Commands & Utilities

from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from db import add_wallet as db_add_wallet, get_wallets as db_get_wallets, remove_wallet as db_remove_wallet

def add_wallet(label, address):
    # Save label/address as tuple in DB or list
    db_add_wallet(label, address)

def get_wallets():
    # Return list of (label, address) tuples
    # Must match what db_get_wallets returns
    return db_get_wallets()

def remove_wallet(label_or_address):
    # Remove by label or address as needed by your db implementation
    db_remove_wallet(label_or_address)

def handle_watch_command(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Usage: /watch <wallet_address> [nickname]")
        return

    address = context.args[0]
    label = " ".join(context.args[1:]) if len(context.args) > 1 else f"Wallet {address[:4]}...{address[-4:]}"
    try:
        add_wallet(label, address)
        update.message.reply_text(f"✅ Watching wallet:\n<code>{address}</code>\nNickname: {label}", parse_mode=ParseMode.HTML)
    except Exception as e:
        update.message.reply_text("⚠️ Error adding wallet.")
        print(f"Error adding wallet: {e}")

def handle_wallets_command(update: Update, context: CallbackContext, via_callback=False):
    wallets = get_wallets()
    if not wallets:
        msg = "No wallets being tracked."
    elif isinstance(wallets[0], tuple):
        msg = "<b>\U0001F4B3 Watched Wallets</b>\n" + "\n".join([f"• {label}\n<code>{addr}</code>" for label, addr in wallets])
    else:
        msg = "<b>\U0001F4B3 Watched Wallets</b>\n" + "\n".join([f"• <code>{addr}</code>" for addr in wallets])

    if via_callback:
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def handle_removewallet_command(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /removewallet <wallet_address or nickname>")
        return

    label_or_address = context.args[0]
    try:
        remove_wallet(label_or_address)
        update.message.reply_text(f"✅ Removed wallet: {label_or_address}")
    except Exception as e:
        update.message.reply_text("⚠️ Error removing wallet.")
        print(f"Error removing wallet: {e}")

def get_wallets_list():
    wallets = get_wallets()
    if not wallets:
        return "No wallets being tracked."
    if isinstance(wallets[0], tuple):
        return "<b>\U0001F4B3 Watched Wallets</b>\n" + "\n".join([f"• {label}\n<code>{addr}</code>" for label, addr in wallets])
    else:
        return "<b>\U0001F4B3 Watched Wallets</b>\n" + "\n".join([f"• <code>{addr}</code>" for addr in wallets])

# --- For main.py compatibility ---
def get_wallet_summary():
    return get_wallets_list()
