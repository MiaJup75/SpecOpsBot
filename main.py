import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from utils import fetch_max_token_data, get_trending_coins, is_allowed
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import json
import os
from flask import Flask, request

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = None
app = Flask(__name__)
scheduler = BackgroundScheduler(timezone=timezone("Asia/Bangkok"))

# Commands
def start(update: Update, context: CallbackContext):
    message = f"""<b>Welcome to SolMadSpecBot!</b>
Here are the available commands:
/max - MAX Token Tracker
/wallets - Watchlist Wallet Activity
/trending - Top 5 Solana Meme Coins
/new - Newly Launched Tokens
/alerts - Suspicious Activity Flags"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def max_token(update: Update, context: CallbackContext):
    if not is_allowed(update, WHITELIST):
        return
    try:
        result = fetch_max_token_data()
        context.bot.send_message(chat_id=update.effective_chat.id, text=result, parse_mode=ParseMode.HTML)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error fetching MAX token data.")
        logger.error(f"MAX command error: {e}")

def trending(update: Update, context: CallbackContext):
    if not is_allowed(update, WHITELIST):
        return
    try:
        result = get_trending_coins()
        context.bot.send_message(chat_id=update.effective_chat.id, text=result, parse_mode=ParseMode.HTML)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error fetching trending coins.")
        logger.error(f"Trending command error: {e}")

def send_daily_report():
    # Placeholder logic
    message = "<b>📊 Daily Report (placeholder)</b>"
    for user_id in WHITELIST:
        try:
            bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Daily report error: {e}")

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dp.process_update(update)
        return "ok"
    return "Webhook Active"

if __name__ == "__main__":
    from telegram import Bot
    from telegram.ext import Dispatcher

    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot, None, workers=1, use_context=True)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("max", max_token))
    dp.add_handler(CommandHandler("trending", trending))

    scheduler.add_job(send_daily_report, "cron", hour=9)
    scheduler.start()

    bot.set_webhook(url=f"https://solmad-spec-bot.onrender.com/")
    logger.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)