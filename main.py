import json
import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import pytz

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]
MAX_TOKEN_ADDRESS = config["max_token"]
WALLETS = config["wallets"]

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Bot command handler
def max_handler(update: Update, context: CallbackContext):
    if str(update.effective_user.id) not in WHITELIST:
        return

    url = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN_ADDRESS}&time_frame=24h"
    response = requests.get(url)
    if response.status_code != 200:
        update.message.reply_text("⚠️ Failed to fetch MAX stats.")
        return

    data = response.json()["data"]
    price = round(float(data["price_usd"]), 6)
    volume = round(float(data["volume_usd"]), 2)
    fdv = round(float(data["fdv"]), 0)

    text = (
        f"🐶 <b>MAX Token Update</b>
"
        f"💰 Price: <b>${price}</b>
"
        f"📊 Volume: <b>${volume:,}</b>
"
        f"📈 FDV: <b>${fdv:,}</b>"
    )
    update.message.reply_text(text, parse_mode="HTML")

# Register command
dispatcher.add_handler(CommandHandler("max", max_handler))

# 9AM daily alert
def send_daily_report():
    text = "📊 Daily MAX token alert (to be extended)"
    for user_id in WHITELIST:
        try:
            bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.error(f"Failed to send daily message to {user_id}: {e}")

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

# Flask route
@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot is live!"

if __name__ == "__main__":
    logger.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)