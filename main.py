import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
)
from db import init_db, add_wallet, get_wallets, add_token, get_tokens, remove_token
from price_alerts import check_price_targets
from stealth_launch import scan_new_tokens
from mirror_watch import check_mirror_wallets
from botnet import check_botnet_activity
from wallet import Wallet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

wallet = Wallet()  # Instantiate wallet once

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 MAX", callback_data='max'),
         InlineKeyboardButton("👛 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("📈 Trending", callback_data='trending'),
         InlineKeyboardButton("🆕 New", callback_data='new')],
        [InlineKeyboardButton("🚨 Alerts", callback_data='alerts'),
         InlineKeyboardButton("📊 PnL", callback_data='pnl')],
        [InlineKeyboardButton("🧠 Meme Sentiment", callback_data='sentiment'),
         InlineKeyboardButton("🤖 Trade Prompt", callback_data='tradeprompt')],
        [InlineKeyboardButton("🔠 Meme Classification", callback_data='classify')],
        [InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch '),
         InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat='/addtoken $')],
        [InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens')],
        [InlineKeyboardButton("🚀 Auto Buy", switch_inline_query_current_chat='/autobuy ')]
    ])

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """<b>👋 Welcome to SolMadSpecBot!</b>

Use the buttons below or type:
/max /wallets /trending  
/new /alerts /debug  
/pnl /sentiment /tradeprompt /classify  
/watch <wallet> [nickname] /addtoken $TOKEN /removetoken $TOKEN /tokens  
/autobuy <TOKEN_SYMBOL> <AMOUNT_SOL>

Daily updates sent at 9AM Bangkok time (GMT+7).""",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

# existing command handlers here...

def autobuy_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 2:
        update.message.reply_text("Usage: /autobuy <TOKEN_SYMBOL> <AMOUNT_SOL>")
        return

    token_symbol = context.args[0].upper()
    try:
        amount = float(context.args[1])
    except ValueError:
        update.message.reply_text("Invalid amount. Please enter a number for the amount of SOL to swap.")
        return

    update.message.reply_text(f"Attempting to buy {amount} SOL worth of {token_symbol}...")

    success = wallet.swap_token(token_symbol, amount)
    if success:
        update.message.reply_text(f"✅ Successfully placed swap order for {amount} SOL to {token_symbol}.")
    else:
        update.message.reply_text(f"❌ Swap failed for {token_symbol}. Check logs for details.")

# Register command handlers
dispatcher.add_handler(CommandHandler("start", start))
# ... your other handlers
dispatcher.add_handler(CommandHandler("autobuy", autobuy_command))

# rest of your main.py code unchanged...

# Scheduler jobs and flask app routes remain as before

if __name__ == '__main__':
    init_db()
    updater.bot.set_my_commands([
        BotCommand("start", "Show welcome message and buttons"),
        # ... other commands ...
        BotCommand("autobuy", "Auto-buy a token with specified SOL amount")
    ])
    app.run(host='0.0.0.0', port=PORT)
