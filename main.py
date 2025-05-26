import json
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
ALLOWED_USERS = config["whitelist"]

app = Flask(__name__)
bot = Bot(token=TOKEN)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Pinned welcome message
WELCOME_MESSAGE = """<b>Welcome to SolMadSpecBot 🧠</b>

Here are the commands you can use:
/max – Get MAX token stats
/wallets – Check tracked wallets
/trending – See top trending coins
/new – Watch <12h new tokens
/alerts – View recent alerts
"""

def start(update: Update, context):
    if str(update.effective_user.id) not in ALLOWED_USERS:
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=WELCOME_MESSAGE,
        parse_mode="HTML"
    )

def set_webhook():
    webhook_url = f"https://solmad-spec-bot.onrender.com/hook"
    bot.set_webhook(url=webhook_url)
    logging.info(f"Webhook set to {webhook_url}")

@app.route("/hook", methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "SolMadSpecBot is running!"

def send_daily_report():
    try:
        message = "<b>📊 Daily Report (placeholder)</b>
Data coming soon."
        bot.send_message(chat_id=ALLOWED_USERS[0], text=message, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error in scheduled report: {e}")

# Dispatcher and handlers
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))

# Scheduler for daily report
scheduler = BackgroundScheduler(timezone=timezone("Asia/Bangkok"))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

# Run the webhook server
if __name__ == "__main__":
    set_webhook()
    logging.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)
