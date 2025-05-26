
from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
import json
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
import os
import pytz

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WALLETS = config["wallets"]
MAX_TOKEN = config["max_token"]
WHITELIST = config["whitelist"]

bot = Bot(token=TOKEN)
app = Flask(__name__)
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))

def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id in WHITELIST:
        update.message.reply_text("✅ Welcome to SolMadSpecBot!")
    else:
        update.message.reply_text("⛔ Access Denied. You are not whitelisted.")

def max(update: Update, context: CallbackContext):
    try:
        url = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN}&time_frame=24h"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        data = response.json()["data"]
        price = round(data["price"], 6)
        fdv = round(data["fdv"], 2)
        volume = round(data["volume"], 2)
        message = (
            f"🐶 <b>MAX Token Update</b>
"
            f"📈 Price: ${price}
"
            f"💰 FDV: ${fdv}
"
            f"📊 Volume (24h): ${volume}
"
            f"https://birdeye.so/token/{MAX_TOKEN}?chain=solana"
        )
        update.message.reply_text(message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"Error in /max command: {e}")
        update.message.reply_text("❌ Failed to fetch MAX token data.")

def send_daily_report():
    try:
        chat_id = WHITELIST[0]
        url = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN}&time_frame=24h"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        data = response.json()["data"]
        price = round(data["price"], 6)
        fdv = round(data["fdv"], 2)
        volume = round(data["volume"], 2)
        message = (
            f"🐶 <b>Daily MAX Token Report</b>
"
            f"📈 Price: ${price}
"
            f"💰 FDV: ${fdv}
"
            f"📊 Volume (24h): ${volume}
"
            f"https://birdeye.so/token/{MAX_TOKEN}?chain=solana"
        )
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"Error in daily report: {e}")

@app.route('/')
def index():
    return "Bot is live."

@app.route('/hook', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("max", max))

    scheduler.add_job(send_daily_report, "cron", hour=9)
    scheduler.start()

    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)
