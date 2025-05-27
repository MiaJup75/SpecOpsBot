import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from flask import Flask, request
import os
import pytz

from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_full_daily_report, HELP_TEXT, simulate_debug_output,
    get_pnl_report, get_sentiment_scores, get_trade_prompt, get_narrative_classification
)
from db import init_db, add_wallet, get_wallets, add_token, get_tokens
from scanner import scan_new_tokens
from stealth_scanner import scan_stealth_tokens
from pnl_tracker import check_max_pnl
from price_alerts import check_price_triggers
from ai_trade import get_ai_trade_prompt
from botnet import detect_botnet_activity
from mirror_watch import check_mirror_trades
from tokens import handle_add_token, handle_tokens, handle_remove_token
from wallets import format_wallet_summary
from apscheduler.schedulers.background import BackgroundScheduler

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

# --- Help Text ---
HELP_TEXT = """
<b>🛠 Available Commands:</b>

/start – Show welcome message and buttons  
/max – View MAX token stats  
/wallets – List watched wallets  
/watch &lt;wallet&gt; – Add a wallet to watch  
/addtoken $TOKEN – Add a token to watch  
/removetoken $TOKEN – Remove a token from watchlist  
/tokens – List all tracked tokens  
/trending – Top trending meme coins  
/new – Newly launched tokens (<24h)  
/alerts – Whale/dev/LP risk alerts  
/pnl – MAX token PnL report  
/sentiment – Meme sentiment scores  
/tradeprompt – AI-generated trade idea  
/classify – Token narrative classifier  
/debug – Simulated debug data

<i>Daily updates sent at 9AM Bangkok time (GMT+7)</i>
"""

# --- UI --- #
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 MAX", callback_data='max'),
         InlineKeyboardButton("👛 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("📈 Trending", callback_data='trending'),
         InlineKeyboardButton("🆕 New", callback_data='new')],
        [InlineKeyboardButton("🚨 Alerts", callback_data='alerts'),
         InlineKeyboardButton("📊 PnL", callback_data='pnl')],
        [InlineKeyboardButton("➕ Add Wallet", switch_inline_query_current_chat='/watch '),
         InlineKeyboardButton("➕ Add Token", switch_inline_query_current_chat='/addtoken $')],
        [InlineKeyboardButton("📋 View Tokens", switch_inline_query_current_chat='/tokens')]
    ])

# --- Commands --- #
def start(update: Update, context: CallbackContext) -> None:
    welcome_text = """<b>👋 Welcome to SolMadSpecBot!</b>

Use the buttons below or type:
/max /wallets /trending  
/new /alerts /debug  
/pnl /sentiment /tradeprompt /classify  
/watch &lt;wallet&gt; /addtoken $TOKEN /tokens

Daily updates sent at 9AM Bangkok time (GMT+7)."""
    update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.HTML)

    # Pin the message for easy reference
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    try:
        context.bot.pin_chat_message(chat_id=chat_id, message_id=message_id, disable_notification=True)
    except Exception as e:
        print(f"Failed to pin message: {e}")

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)

def panel_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("🔘 <b>SolMadSpecBot Panel</b>\nTap a button below:",
                              reply_markup=get_main_keyboard(), parse_mode=ParseMode.HTML)

def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    command = query.data

    func_map = {
        'max': get_max_token_stats,
        'wallets': format_wallet_summary,
        'trending': get_trending_coins,
        'new': get_new_tokens,
        'alerts': get_suspicious_activity_alerts,
        'pnl': get_pnl_report
    }

    result = func_map.get(command, lambda: "Unknown command")()
    context.bot.send_message(chat_id=query.message.chat.id, text=result, parse_mode=ParseMode.HTML)

def watch_command(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            update.message.reply_text("Usage: /watch &lt;wallet_address&gt;", parse_mode=ParseMode.HTML)
            return
        address = context.args[0]
        label = f"Wallet {address[:4]}...{address[-4:]}"
        add_wallet(label, address)
        update.message.reply_text(f"✅ Watching wallet:\n<code>{address}</code>", parse_mode=ParseMode.HTML)
    except Exception:
        update.message.reply_text("⚠️ Error adding wallet.")

def wallets_command(update: Update, context: CallbackContext) -> None:
    summary = format_wallet_summary()
    update.message.reply_text(summary, parse_mode=ParseMode.HTML)

# --- Handlers --- #
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("panel", panel_command))
dispatcher.add_handler(CommandHandler("max", lambda u, c: u.message.reply_text(get_max_token_stats(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("watch", watch_command))
dispatcher.add_handler(CommandHandler("addtoken", handle_add_token))
dispatcher.add_handler(CommandHandler("tokens", handle_tokens))
dispatcher.add_handler(CommandHandler("removetoken", handle_remove_token))
dispatcher.add_handler(CommandHandler("trending", lambda u, c: u.message.reply_text(get_trending_coins(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("new", lambda u, c: u.message.reply_text(get_new_tokens(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("alerts", lambda u, c: u.message.reply_text(get_suspicious_activity_alerts(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("debug", lambda u, c: u.message.reply_text(simulate_debug_output(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("pnl", lambda u, c: u.message.reply_text(get_pnl_report(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("sentiment", lambda u, c: u.message.reply_text(get_sentiment_scores(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CommandHandler("tradeprompt", lambda u, c: get_ai_trade_prompt(c.bot)))
dispatcher.add_handler(CommandHandler("classify", lambda u, c: u.message.reply_text(get_narrative_classification(), parse_mode=ParseMode.HTML)))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

# --- Scheduler Jobs --- #
def send_daily_report(bot):
    chat_id = os.getenv("CHAT_ID")
    report = get_full_daily_report()
    bot.send_message(chat_id=chat_id, text=report, parse_mode=ParseMode.HTML)

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
scheduler.add_job(lambda: send_daily_report(dispatcher.bot), 'cron', hour=9, minute=0)
scheduler.add_job(lambda: scan_new_tokens(dispatcher.bot), 'interval', minutes=5)
scheduler.add_job(lambda: scan_stealth_tokens(dispatcher.bot), 'interval', minutes=7)
scheduler.add_job(lambda: check_max_pnl(dispatcher.bot), 'interval', minutes=10)
scheduler.add_job(lambda: check_price_triggers(dispatcher.bot), 'interval', minutes=7)
scheduler.add_job(lambda: get_ai_trade_prompt(dispatcher.bot), 'interval', minutes=15)
scheduler.add_job(lambda: detect_botnet_activity(dispatcher.bot), 'interval', minutes=20)
scheduler.add_job(lambda: check_mirror_trades(dispatcher.bot), 'interval', minutes=18)
scheduler.start()

# --- Webhook Setup --- #
@app.route('/')
def index():
    return "SolMadSpecBot is running."

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return 'ok'

# --- Run --- #
if __name__ == '__main__':
    init_db()
    updater.bot.set_my_commands([
        BotCommand("start", "Show welcome message and buttons"),
        BotCommand("help", "Show this help message"),
        BotCommand("max", "Show MAX token stats"),
        BotCommand("wallets", "List all watched wallets"),
        BotCommand("watch", "Add a new wallet to watch"),
        BotCommand("addtoken", "Add a token to watch"),
        BotCommand("tokens", "List all tracked tokens"),
        BotCommand("removetoken", "Remove a tracked token"),
        BotCommand("trending", "View top trending meme coins"),
        BotCommand("new", "Show new token launches"),
        BotCommand("alerts", "Show whale/dev/suspicious alerts"),
        BotCommand("pnl", "Check your MAX token PnL"),
        BotCommand("sentiment", "See meme sentiment scores"),
        BotCommand("tradeprompt", "AI-generated trade idea"),
        BotCommand("classify", "Classify token narratives"),
        BotCommand("debug", "Run simulated debug outputs")
    ])
    app.run(host='0.0.0.0', port=PORT)
