import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import json
import pytz

from utils import (
    fetch_max_token_data,
    is_allowed,
    get_trending_coins,
    get_new_tokens,
    check_suspicious_activity,
    get_wallet_activity,
    get_post_launch_scorecard
)

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]
bot = Bot(token=TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=1, use_context=True)

def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        update.message.reply_text("❌ You are not authorized to use this bot.")
        return

    message = (
        "<b>Welcome to SolMadSpecBot!</b>

"
        "Available Commands:
"
        "/max - View MAX token stats
"
        "/trending - Top 5 trending Solana meme coins
"
        "/new - New tokens (<12h old)
"
        "/alerts - Suspicious activity alerts
"
        "/wallets - Monitored wallet activity
"
        "/score - Post-launch scorecard"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def max(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return
    try:
        message = fetch_max_token_data()
        context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in /max: {e}")
        update.message.reply_text("⚠️ Failed to fetch MAX token data.")

def trending(update: Update, context: CallbackContext):
    coins = get_trending_coins()
    context.bot.send_message(chat_id=update.effective_chat.id, text=coins, parse_mode="HTML")

def new_tokens(update: Update, context: CallbackContext):
    tokens = get_new_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=tokens, parse_mode="HTML")

def alerts(update: Update, context: CallbackContext):
    alert = check_suspicious_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=alert, parse_mode="HTML")

def wallets(update: Update, context: CallbackContext):
    activity = get_wallet_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=activity, parse_mode="HTML")

def scorecard(update: Update, context: CallbackContext):
    score = get_post_launch_scorecard()
    context.bot.send_message(chat_id=update.effective_chat.id, text=score, parse_mode="HTML")

@app.route(f"/hook", methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "SolMadSpecBot is alive!"

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("new", new_tokens))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("score", scorecard))

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
scheduler.start()

def send_daily_report():
    try:
        for user_id in WHITELIST:
            message = "<b>📊 Daily Report (placeholder)</b>

Use /max, /trending, /new, /alerts, /wallets or /score."
            bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error sending daily report: {e}")

scheduler.add_job(send_daily_report, "cron", hour=9)

if __name__ == "__main__":
    logger.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)