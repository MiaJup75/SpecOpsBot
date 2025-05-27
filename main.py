import logging
import json
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from utils import (
    fetch_max_token_data,
    is_allowed,
    get_trending_coins,
    get_new_tokens,
    check_suspicious_activity,
    get_wallet_activity,
)

# Load config
with open("config.json") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config.get("whitelist", [])
bot = Bot(token=TOKEN)
app = Flask(__name__)
scheduler = BackgroundScheduler()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dispatcher = Dispatcher(bot, None, use_context=True)

# Command handlers
def start(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    keyboard = [
        [InlineKeyboardButton("MAX Token", callback_data="/max")],
        [InlineKeyboardButton("Wallets", callback_data="/wallets")],
        [InlineKeyboardButton("Trending", callback_data="/trending")],
        [InlineKeyboardButton("New Tokens", callback_data="/new")],
        [InlineKeyboardButton("Suspicious Alerts", callback_data="/alerts")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = (
        "<b>Welcome to SolMadSpecBot!</b>\n\n"
        "Available Commands:\n"
        "/max – View MAX token data\n"
        "/wallets – Track tagged wallet activity\n"
        "/trending – Top trending meme coins\n"
        "/new – Newly launched Sol tokens\n"
        "/alerts – Suspicious activity alerts\n"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

def help_command(update: Update, context):
    return start(update, context)

def max_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    message = fetch_max_token_data()
    update.message.reply_text(message, parse_mode="HTML")

def trending_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    message = get_trending_coins()
    update.message.reply_text(message, parse_mode="HTML")

def new_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    message = get_new_tokens()
    update.message.reply_text(message, parse_mode="HTML")

def alerts_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    message = check_suspicious_activity()
    update.message.reply_text(message, parse_mode="HTML")

def wallets_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    message = get_wallet_activity()
    update.message.reply_text(message, parse_mode="HTML")

# Callback from buttons
def handle_button(update: Update, context):
    data = update.callback_query.data
    update.callback_query.answer()
    update.message = update.callback_query.message
    if data == "/max":
        max_command(update, context)
    elif data == "/wallets":
        wallets_command(update, context)
    elif data == "/trending":
        trending_command(update, context)
    elif data == "/new":
        new_command(update, context)
    elif data == "/alerts":
        alerts_command(update, context)

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("trending", trending_command))
dispatcher.add_handler(CommandHandler("new", new_command))
dispatcher.add_handler(CommandHandler("alerts", alerts_command))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("start", start))

# Daily 9AM report
def send_daily_report():
    for user in WHITELIST:
        try:
            bot.send_message(chat_id=user, text="<b>📊 Daily Report (placeholder)</b>", parse_mode="HTML")
        except Exception as e:
            logger.warning(f"Failed to send daily report: {e}")

scheduler.add_job(send_daily_report, "cron", hour=9, timezone="Asia/Bangkok")
scheduler.start()

@app.route("/")
def index():
    return "OK"

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

if __name__ == "__main__":
    logging.info("Running SolMadSpecBot...")
    bot.set_webhook(url="https://solmad-spec-bot.onrender.com/hook")
    app.run(host="0.0.0.0", port=10000)
