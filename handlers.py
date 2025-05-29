# handlers.py – Command Router

from telegram.ext import CommandHandler, CallbackQueryHandler, Dispatcher

from start_help import handle_start, handle_help
from alerts import handle_alerts_command
from trending import handle_trending_command
from tokens import handle_addtoken_command, handle_tokens_command, handle_removetoken_command
from wallet_db import handle_watch_command, handle_wallets_command
from sentiment import handle_sentiment_command
from pnl import handle_pnl_command
from scorecard import handle_scorecard_command

# Optional: inline button callbacks
try:
    from callbacks import handle_button_callback
except ImportError:
    handle_button_callback = None

def register_handlers(dp: Dispatcher):
    dp.add_handler(CommandHandler("start", handle_start))
    dp.add_handler(CommandHandler("help", handle_help))

    # Tier 1
    dp.add_handler(CommandHandler("alerts", handle_alerts_command))
    dp.add_handler(CommandHandler("trending", handle_trending_command))

    # Tier 2
    dp.add_handler(CommandHandler("watch", handle_watch_command))
    dp.add_handler(CommandHandler("wallets", handle_wallets_command))
    dp.add_handler(CommandHandler("scorecard", handle_scorecard_command))

    # Tier 3
    dp.add_handler(CommandHandler("pnl", handle_pnl_command))
    dp.add_handler(CommandHandler("sentiment", handle_sentiment_command))

    # Tier 5
    dp.add_handler(CommandHandler("addtoken", handle_addtoken_command))
    dp.add_handler(CommandHandler("tokens", handle_tokens_command))
    dp.add_handler(CommandHandler("removetoken", handle_removetoken_command))

    # Optional: handle inline button callbacks
    if handle_button_callback:
        dp.add_handler(CallbackQueryHandler(handle_button_callback))
