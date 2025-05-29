# start_help.py – Start & Help Command Handler

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

WELCOME_MESSAGE = """
<b>👋 Welcome to SolMadSpecBot</b>

This bot helps you track Solana meme coins, whale wallets, and suspicious activity in real time.

<b>Available Commands:</b>
/start – Show this message
/help – List all commands
/max – View MAX token stats
/wallets – Show tracked wallets
/watch – Add a wallet to watch
/addtoken – Watch a token (e.g. /addtoken $DOGE)
/tokens – Show watched tokens
/removetoken – Stop watching a token
/trending – Show top trending Solana tokens
/new – Show newly launched tokens
/alerts – Show suspicious activity alerts
/pnl – Show your PnL summary
/scorecard – Generate a token scorecard
"""

def handle_start_command(update: Update, context: CallbackContext):
    update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.HTML)

def handle_help_command(update: Update, context: CallbackContext):
    update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.HTML)
