
import json
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler, Dispatcher
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
MAX_TOKEN = config["max_token"]
ALLOWED_USERS = set(config["whitelist"])

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

def is_allowed(user_id):
    return str(user_id) in ALLOWED_USERS

def fetch_max_token_data():
    url = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN}&time_frame=24h"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.ok:
        data = response.json().get("data", {})
        price = data.get("price", 0)
        market_cap = data.get("market_cap", 0)
        volume = data.get("volume_24h", 0)
        fdv = data.get("fdv", 0)
        return price, market_cap, volume, fdv
    return 0, 0, 0, 0

def max_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    price, market_cap, volume, fdv = fetch_max_token_data()
    message = (
        f"🐶 <b>MAX Token Update</b>
"
        f"💰 Price: ${price:.8f}
"
        f"📊 Market Cap: ${market_cap:,.0f}
"
        f"📈 Volume (24h): ${volume:,.0f}
"
        f"🏦 FDV: ${fdv:,.0f}"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

dispatcher.add_handler(CommandHandler("max", max_command))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

def send_daily_report():
    price, market_cap, volume, fdv = fetch_max_token_data()
    message = (
        f"🌅 <b>Daily MAX Token Report</b>
"
        f"💰 Price: ${price:.8f}
"
        f"📊 Market Cap: ${market_cap:,.0f}
"
        f"📈 Volume (24h): ${volume:,.0f}
"
        f"🏦 FDV: ${fdv:,.0f}"
    )
    for user_id in ALLOWED_USERS:
        bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
    scheduler.add_job(send_daily_report, "cron", hour=9)
    scheduler.start()
    logging.info("🔄 Starting webhook server...")
    bot.set_webhook(url=f"https://solmad-spec-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)
