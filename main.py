import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from utils import (
    get_max_token_stats, get_trending_coins, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification,
    # We'll add our new helper here for fetching token info dynamically
    fetch_token_info
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
        [InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens')]
    ])

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """<b>👋 Welcome to SolMadSpecBot!</b>

Use the buttons below or type:
/max /wallets /trending  
/new /alerts /debug  
/pnl /sentiment /tradeprompt /classify  
/watch &lt;wallet&gt; /addtoken $TOKEN /tokens

Daily updates sent at 9AM Bangkok time (GMT+7).""",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

def panel_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🔘 <b>SolMadSpecBot Panel</b>\nTap a button below:",
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

def build_token_button(symbol: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=f"${symbol}", callback_data=f"token_{symbol}")

def new_tokens_command(update: Update, context: CallbackContext) -> None:
    # Sample tokens info list - you will replace this with actual data source
    tokens_info = [
        {"symbol": "LOOT", "lp": "8.4K", "lock_status": "Locked 7d", "unlock_time": None},
        {"symbol": "ZOOM", "lp": "5.9K", "lock_status": "Unlocks in 12h", "unlock_time": "12h"},
        {"symbol": "RUGME", "lp": "3.1K", "lock_status": "No lock", "unlock_time": None},
    ]
    chat_id = update.message.chat_id
    buttons = []
    lines = []
    for token in tokens_info:
        buttons.append([build_token_button(token["symbol"])])
        unlock_text = f" – {token['lock_status']}"
        line = f"• ${token['symbol']} – LP ${token['lp']}{unlock_text}"
        lines.append(line)
    keyboard = InlineKeyboardMarkup(buttons)
    message_text = "<b>New Token Launches (&lt;24h)</b>\n\n" + "\n".join(lines) + "\n\nClick /alerts for suspicious flags"
    update.message.reply_text(message_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

def handle_token_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    symbol = query.data.split("_", 1)[1]
    token_info = fetch_token_info(symbol)
    if not token_info:
        query.answer("Token info not found.", show_alert=True)
        return
    dex_link = f"https://dexscreener.com/solana/{token_info.get('pair', '')}"
    details = (
        f"<b>{symbol}</b>\n"
        f"Price: ${token_info.get('price', 'N/A')}\n"
        f"Market Cap: ${token_info.get('market_cap', 'N/A')}\n"
        f"Liquidity: ${token_info.get('liquidity', 'N/A')}\n"
        f"<a href='{dex_link}'>View on Dexscreener</a>"
    )
    query.edit_message_text(text=details, parse_mode=ParseMode.HTML, disable_web_page_preview=False)

# ... rest of your existing commands and handlers ...

# Replace the "new" command handler to use our updated one
dispatcher.add_handler(CommandHandler("new", new_tokens_command))

# Add the token callback handler for inline button presses
dispatcher.add_handler(CallbackQueryHandler(handle_token_callback, pattern=r"^token_"))

# other handlers registrations (start, max, wallets, watch, addtoken, tokens, removetoken, trending, alerts, debug, pnl, sentiment, tradeprompt, classify, panel)...

# Scheduler and webhook setup code unchanged

# Your usual main run and setup code here...
