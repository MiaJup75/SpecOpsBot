import json
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
MAX_TOKEN = config["max_token"]
WHITELIST = config["whitelist"]
bot = Bot(token=TOKEN)

# Logging
logging.basicConfig(level=logging.INFO)

# Flask app
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)

# /start handler
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        return
    update.message.reply_text("🤖 Welcome to SolMadSpecBot!\nTracking wallets, MAX token & meme coins daily...")

# /max handler
def max_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        return

    try:
        logging.info("Fetching MAX token price...")
        response = requests.get(
            f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN}&time_frame=24h",
            headers={"X-API-KEY": "public"}
        )
        data = response.json().get("data", {})

        price = float(data.get("price", 0))
        market_cap = round(price * 1_000_000_000, 2)

        message = f"🌐 MAX Token Info:\nPrice: ${price:.9f}\nMarket Cap: ${market_cap:,.2f}"
    except Exception as e:
        logging.error("Error fetching MAX data: %s", e)
        message = f"⚠️ Error fetching MAX data: {e}"

    update.message.reply_text(message)

# Webhook route
@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Bind handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_command))

# Scheduler (optional)
def send_daily_report():
    logging.info("Sending daily report placeholder")

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

# Main entry point
if __name__ == "__main__":
    logging.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)
