from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher
from flask import Flask, request
import json
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from utils import fetch_max_token_data, is_allowed, get_trending_coins

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load config
with open("config.json") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=1)

@app.route("/")
def index():
    return "Bot is running!"

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

def start(update, context):
    message = """<b>Welcome to SolMadSpecBot!</b>

Choose a command:
/max – MAX Token stats & alerts
/wallets – Watchlist wallet activity
/trending – Top 5 SOL meme coins
/new – Just launched tokens (under 12h)
/alerts – Suspicious bot/dev/Liquidity moves"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def max_command(update, context):
    if not is_allowed(update.effective_user.id, WHITELIST):
        return
    token_data = fetch_max_token_data()
    if not token_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Unable to fetch MAX token data.")
        return
    message = f"""🐶 <b>MAX Token Update</b>

💰 Price: ${token_data['price_usd']}
📊 Volume (24h): ${token_data['volume_usd']}
💧 Liquidity: ${token_data['liquidity_usd']}
🏷️ FDV: ${token_data['fdv']}
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def send_daily_report():
    logger.info("Sending placeholder daily report.")
    # Implement daily alert message content here

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_command))

# Schedule daily report at 9AM Bangkok time
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

if __name__ == "__main__":
    logger.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)
