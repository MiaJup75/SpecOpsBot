import json
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from utils import fetch_max_token_data, is_allowed

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="🤖 SolMadSpecBot is online!")

def max_command(update: Update, context):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        return

    try:
        data = fetch_max_token_data()
        if not data:
            update.message.reply_text("⚠️ Unable to fetch MAX token data.")
            return

        price = data.get("price", "N/A")
        market_cap = data.get("market_cap", "N/A")
        volume = data.get("volume_24h", "N/A")
        fdv = data.get("fdv", "N/A")

        message = f"""
🐶 <b>MAX Token Update</b>
• 💰 Price: ${price}
• 📈 Market Cap: ${market_cap}
• 📊 Volume (24h): ${volume}
• 🧮 FDV: ${fdv}
"""
        update.message.reply_text(message, parse_mode='HTML')

    except Exception as e:
        logger.error(f"/max command failed: {e}")
        update.message.reply_text("❌ An error occurred while fetching data.")

def send_daily_report():
    try:
        data = fetch_max_token_data()
        if not data:
            return

        price = data.get("price", "N/A")
        market_cap = data.get("market_cap", "N/A")
        volume = data.get("volume_24h", "N/A")
        fdv = data.get("fdv", "N/A")

        message = f"""
📅 <b>Daily MAX Token Report</b>
• 💰 Price: ${price}
• 📈 Market Cap: ${market_cap}
• 📊 Volume (24h): ${volume}
• 🧮 FDV: ${fdv}
"""

        for user_id in WHITELIST:
            bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Daily report failed: {e}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_command))

@app.route("/")
def index():
    return "SolMadSpecBot is running!"

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Schedule daily report
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=9, timezone=timezone("Asia/Bangkok"))
scheduler.start()

if __name__ == "__main__":
    logger.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)