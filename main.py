import json
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update, ParseMode
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
MAX_TOKEN = config["max_token"]
WHITELIST = config["whitelist"]

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def start(update: Update, context):
    user_id = str(update.effective_user.id)
    if user_id in WHITELIST:
        update.message.reply_text("👋 Welcome to SolMadSpecBot! Use /max for token stats.")
    else:
        update.message.reply_text("⛔ Access denied. You're not whitelisted.")

def max_command(update: Update, context):
    url = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN}&time_frame=24h"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", {})
        price = data.get("price", 0)
        fdv = data.get("fdv", 0)
        volume = data.get("volume", 0)

        message = (
            f"🐶 <b>MAX Token Update</b>
"
            f"💰 Price: ${price:.8f}
"
            f"📈 Volume: ${volume:,.0f}
"
            f"🏦 FDV: ${fdv:,.0f}"
        )
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text("Failed to fetch MAX token data.")

def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "ok"
    return "pong"

@app.route("/")
def index():
    return "Bot is running"

@app.route("/hook", methods=["POST", "GET"])
def handle_webhook():
    return webhook()

def send_daily_report():
    try:
        url = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN}&time_frame=24h"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json().get("data", {})
            price = data.get("price", 0)
            fdv = data.get("fdv", 0)
            volume = data.get("volume", 0)

            message = (
                f"🐶 <b>MAX Token Update</b>
"
                f"💰 Price: ${price:.8f}
"
                f"📈 Volume: ${volume:,.0f}
"
                f"🏦 FDV: ${fdv:,.0f}"
            )

            for uid in WHITELIST:
                bot.send_message(chat_id=uid, text=message, parse_mode=ParseMode.HTML)
        else:
            logger.error("Failed to fetch data for report.")
    except Exception as e:
        logger.error(f"Error in send_daily_report: {e}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_command))

scheduler = BackgroundScheduler(timezone=timezone("Asia/Bangkok"))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

if __name__ == "__main__":
    logger.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)
