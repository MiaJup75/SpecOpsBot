import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from utils import (
    get_max_token_stats, get_trending_coins, get_new_tokens, get_suspicious_activity_alerts,
    get_wallet_summary, get_full_daily_report, HELP_TEXT, simulate_debug_output
)
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
import os

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

# --- Command Handlers --- #

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("💰 MAX", callback_data='max'),
         InlineKeyboardButton("👛 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("📈 Trending", callback_data='trending'),
         InlineKeyboardButton("🆕 New", callback_data='new')],
        [InlineKeyboardButton("🚨 Alerts", callback_data='alerts'),
         InlineKeyboardButton("🧪 Debug", callback_data='debug')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_message = """
<b>👋 Welcome to SolMadSpecBot!</b>

Use the buttons below or type a command:
/max – MAX token stats  
/wallets – Watchlist activity  
/trending – Top meme coins  
/new – New token launches  
/alerts – Suspicious activity  
/debug – Simulated data

Daily updates sent at 9AM Bangkok time.
"""
    update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    command = query.data

    if command == 'max':
        query.edit_message_text(get_max_token_stats(), parse_mode=ParseMode.HTML)
    elif command == 'wallets':
        query.edit_message_text(get_wallet_summary(), parse_mode=ParseMode.HTML)
    elif command == 'trending':
        query.edit_message_text(get_trending_coins(), parse_mode=ParseMode.HTML)
    elif command == 'new':
        query.edit_message_text(get_new_tokens(), parse_mode=ParseMode.HTML)
    elif command == 'alerts':
        query.edit_message_text(get_suspicious_activity_alerts(), parse_mode=ParseMode.HTML)
    elif command == 'debug':
        query.edit_message_text(simulate_debug_output(), parse_mode=ParseMode.HTML)

def max_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_max_token_stats(), parse_mode=ParseMode.HTML)

def wallets_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_wallet_summary(), parse_mode=ParseMode.HTML)

def trending_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_trending_coins(), parse_mode=ParseMode.HTML)

def new_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_new_tokens(), parse_mode=ParseMode.HTML)

def alerts_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(get_suspicious_activity_alerts(), parse_mode=ParseMode.HTML)

def debug_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(simulate_debug_output(), parse_mode=ParseMode.HTML)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)

# --- Scheduler Job --- #

def send_daily_report(bot):
    chat_id = os.getenv("CHAT_ID")
    report = get_full_daily_report()
    bot.send_message(chat_id=chat_id, text=report, parse_mode=ParseMode.HTML)

# --- Register Handlers --- #

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("trending", trending_command))
dispatcher.add_handler(CommandHandler("new", new_command))
dispatcher.add_handler(CommandHandler("alerts", alerts_command))
dispatcher.add_handler(CommandHandler("debug", debug_command))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

# --- Scheduler Setup --- #

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: send_daily_report(dispatcher.bot), 'cron', hour=9, minute=0, timezone='Asia/Bangkok')
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

updater.bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
