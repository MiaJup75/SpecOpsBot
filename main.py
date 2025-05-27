import logging
import pytz
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
from utils import (
    fetch_max_token_data,
    get_trending_coins,
    fetch_new_tokens,
    check_suspicious_activity,
    summarize_wallet_activity,
    track_position,
    send_target_alerts,
)
import os

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]

bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for webhook
app = Flask(__name__)

# Pinned welcome message
WELCOME_MSG = """
<b>Welcome to SolMadSpecBot!</b>

Use the commands below to explore:

/max – MAX token update  
/trending – Top 5 meme coins  
/new – Newly launched tokens  
/alerts – Suspicious activity  
/wallets – Tracked wallet activity  
/help – View this list again  
"""

# Inline keyboard
keyboard = [
    [InlineKeyboardButton("🪙 MAX Update", callback_data="max")],
    [InlineKeyboardButton("📈 Trending", callback_data="trending")],
    [InlineKeyboardButton("🆕 New", callback_data="new")],
    [InlineKeyboardButton("⚠️ Alerts", callback_data="alerts")],
    [InlineKeyboardButton("👛 Wallets", callback_data="wallets")],
]
reply_markup = InlineKeyboardMarkup(keyboard)

def is_allowed(user_id):
    return str(user_id) in WHITELIST

# Command handlers
def start(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=WELCOME_MSG,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

def help_command(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        return
    update.message.reply_text(WELCOME_MSG, parse_mode="HTML", reply_markup=reply_markup)

def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "max":
        fetch_max_token_data(query.message.chat_id)
    elif query.data == "trending":
        get_trending_coins(query.message.chat_id)
    elif query.data == "new":
        fetch_new_tokens(query.message.chat_id)
    elif query.data == "alerts":
        check_suspicious_activity(query.message.chat_id)
    elif query.data == "wallets":
        summarize_wallet_activity(query.message.chat_id)

# Daily summary
def send_daily_report():
    for user_id in WHITELIST:
        get_trending_coins(user_id)
        fetch_new_tokens(user_id)
        check_suspicious_activity(user_id)
        fetch_max_token_data(user_id)
        summarize_wallet_activity(user_id)

# Routes
@app.route("/", methods=["GET"])
def index():
    return "Running SolMadSpecBot..."

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Webhook init
def set_webhook():
    URL = os.environ.get("WEBHOOK_URL")
    if URL:
        bot.set_webhook(f"{URL}/hook")
        print(f"Webhook set to {URL}/hook")

# Command map
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("max", lambda u, c: fetch_max_token_data(u.effective_chat.id)))
dispatcher.add_handler(CommandHandler("trending", lambda u, c: get_trending_coins(u.effective_chat.id)))
dispatcher.add_handler(CommandHandler("new", lambda u, c: fetch_new_tokens(u.effective_chat.id)))
dispatcher.add_handler(CommandHandler("alerts", lambda u, c: check_suspicious_activity(u.effective_chat.id)))
dispatcher.add_handler(CommandHandler("wallets", lambda u, c: summarize_wallet_activity(u.effective_chat.id)))
dispatcher.add_handler(CommandHandler("pnl", lambda u, c: track_position(u.effective_chat.id)))
dispatcher.add_handler(CommandHandler("targets", lambda u, c: send_target_alerts(u.effective_chat.id)))
dispatcher.add_handler(CallbackQueryHandler(handle_button))

# Daily job
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

if __name__ == "__main__":
    print("Running SolMadSpecBot...")
    set_webhook()
    app.run(host="0.0.0.0", port=10000)
