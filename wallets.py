# wallets.py – Wallet Tracker Commands & Utilities

from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from db import add_wallet, get_wallets, remove_wallet

def handle_watch_command(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /watch WALLET_ADDRESS")
        return

    wallet_address = context.args[0]
    try:
        add_wallet(wallet_address)
        update.message.reply_text(f"✅ Watching wallet: {wallet_address}")
    except Exception as e:
        update.message.reply_text("⚠️ Error adding wallet.")
        print(f"Error adding wallet: {e}")

def handle_wallets_command(update: Update, context: CallbackContext, via_callback=False):
    wallets = get_wallets()
    if not wallets:
        msg = "No wallets being watched."
    else:
        wallet_list = "\n".join([f"• <code>{w}</code>" for w in wallets])
        msg = f"<b>👀 Watched Wallets</b>\n{wallet_list}"

    if via_callback:
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def handle_removewallet_command(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /removewallet WALLET_ADDRESS")
        return

    wallet_address = context.args[0]
    try:
        remove_wallet(wallet_address)
        update.message.reply_text(f"✅ Removed wallet: {wallet_address}")
    except Exception as e:
        update.message.reply_text("⚠️ Error removing wallet.")
        print(f"Error removing wallet: {e}")

def get_wallets_list():
    wallets = get_wallets()
    if not wallets:
        return "No wallets being watched."

    return "<b>👀 Watched Wallets</b>\n" + "\n".join([f"• <code>{w}</code>" for w in wallets])
