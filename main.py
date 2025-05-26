from telegram import Update, ParseMode
from telegram.ext import CommandHandler
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import json

from utils import fetch_max_token_data, is_allowed

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

with open("config.json") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]

def max_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return

    price, market_cap, volume, fdv = fetch_max_token_data()
    message = f"""🐶 <b>MAX Token Update</b>

💵 <b>Price:</b> ${price:.8f}
🏦 <b>Market Cap:</b> ${market_cap:,.0f}
📊 <b>Volume (24h):</b> ${volume:,.0f}
🧠 <b>FDV:</b> ${fdv:,.0f}
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

from telegram import Bot
from telegram.ext import Dispatcher, CallbackContext

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("max", max_command))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def index():
    return "SolMadSpecBot is running!"

def send_daily_report():
    # Placeholder for future daily tasks
    pass

scheduler.add_job(send_daily_report, "cron", hour=9)
