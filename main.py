import logging
from flask import Flask, request
from telegram import Bot, Update, ParseMode
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
import json

# Load config
with open("config.json") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

def start(update: Update, context):
    chat_id = str(update.effective_chat.id)
    if chat_id in WHITELIST:
        welcome_message = (
            "<b>🤖 SolMadSpecBot Activated</b>\n"
            "Use the commands below:\n"
            "/max – MAX Token update\n"
            "/wallets – Wallet alerts\n"
            "/trending – Top meme coins\n"
            "/new – New token watch\n"
            "/alerts – Suspicious activity"
        )
        bot.send_message(chat_id=chat_id, text=welcome_message, parse_mode=ParseMode.HTML)
    else:
        bot.send_message(chat_id=chat_id, text="❌ Not authorized.")

def max_command(update: Update, context):
    chat_id = str(update.effective_chat.id)
    if chat_id in WHITELIST:
        message = (
            "<b>🐶 MAX Token Update</b>\n"
            "<i>Live stats will appear here once API fixes complete.</i>"
        )
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)

def send_daily_report():
    for user_id in WHITELIST:
        message = """<b>📊 Daily Report (placeholder)</b>
<i>Coming soon: volume, LP, and trend highlights.</i>"""
        bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_command))

@app.route(f'/{TOKEN}', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def index():
    return "SolMadSpecBot is live!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_report, "cron", hour=9)
    scheduler.start()
    app.run(host="0.0.0.0", port=10000)
