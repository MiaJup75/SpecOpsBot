# tokens.py – Tier 5.2 Coins Held View

from db import get_wallets
from utils import get_spl_tokens_from_wallet, get_token_stats, format_token_stats
from telegram import Update
from telegram.ext import CallbackContext

def handle_tokens_command(update: Update, context: CallbackContext, via_callback=False):
    wallets = get_wallets()
    
    if not wallets:
        message = "<b>Coins Held:</b>\n\n<i>No wallets are being tracked yet.</i>\nUse /watch to add one."
        _send_response(update, message, via_callback)
        return

    all_tokens = []
    for label, wallet in wallets:
        tokens = get_spl_tokens_from_wallet(wallet)
        if not tokens:
            continue
        token_lines = []
        for token in tokens:
            try:
                stats = get_token_stats(token['address'])
                token_lines.append(format_token_stats(stats, label=label))
            except Exception:
                token_lines.append(f"⚠️ Failed to load stats for {token['symbol']}")
        if token_lines:
            all_tokens.append(f"<b>👛 {label}</b>\n" + "\n".join(token_lines))

    if not all_tokens:
        message = "<b>Coins Held:</b>\n\n<i>No tokens found with non-zero balances in tracked wallets.</i>"
    else:
        message = "<b>Coins Held:</b>\n\n" + "\n\n".join(all_tokens)

    _send_response(update, message, via_callback)

def _send_response(update, message, via_callback):
    if via_callback:
        update.callback_query.edit_message_text(message, parse_mode='HTML', disable_web_page_preview=True)
    else:
        update.message.reply_text(message, parse_mode='HTML', disable_web_page_preview=True)
