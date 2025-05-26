# main.py (simplified for deployment)
from telegram import Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
import logging, json, os
from utils import fetch_max_token_data, is_allowed

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
bot = Bot(token=TOKEN)
app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

def send_daily_report():
    try:
        data = fetch_max_token_data()
        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${data['price']}
📊 Market Cap: ${data['market_cap']}
💧 Liquidity: ${data['liquidity']}
📈 24h Volume: ${data['volume']}
📅 FDV: ${data['fdv']}"""
        for uid in config["whitelist"]:
            bot.send_message(chat_id=uid, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Daily report error: {e}")

@app.route("/")
def index():
    return "SolMadSpecBot is running."

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Welcome to SolMadSpecBot!\nUse /max to check MAX token status.")

def max_command(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        return
    try:
        data = fetch_max_token_data()
        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${data['price']}
📊 Market Cap: ${data['market_cap']}
💧 Liquidity: ${data['liquidity']}
📈 24h Volume: ${data['volume']}
📅 FDV: ${data['fdv']}"""
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
    except Exception as e:
        update.message.reply_text(f"Error fetching data: {e}")

if __name__ == "__main__":
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("max", max_command))
    bot.set_webhook(url="https://solmad-spec-bot.onrender.com/hook")
    scheduler.add_job(send_daily_report, "cron", hour=9, timezone="Asia/Bangkok")
    app.run(host="0.0.0.0", port=10000)
