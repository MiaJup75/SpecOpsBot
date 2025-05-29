# callbacks.py – Inline Callback Handlers

from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from tokens import handle_tokens_command
from wallets import handle_wallets_command


def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == "view_tokens":
        handle_tokens_command(update, context, via_callback=True)
    elif data == "view_wallets":
        handle_wallets_command(update, context, via_callback=True)
    else:
        query.edit_message_text(text="Unknown command.")

    query.answer()
