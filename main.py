
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, request
import json
from utils import fetch_max_token_data, is_allowed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("config.json") as f:
    config = json.load(f)

bot = Bot(token=config["telegram_token"])

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "SolMadSpecBot Webhook Active!"

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

def start(update: Update, context: CallbackContext) -> None:
    message = (
        "<b>Welcome to SolMadSpecBot!</b>
"
        "/max - Get MAX token stats
"
        "/trending - Trending meme coins
"
        "/new - New tokens (<12h old)
"
        "/alerts - Suspicious wallet/LP activity
"
        "/wallets - Tracked wallet activity"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def max(update: Update, context: CallbackContext) -> None:
    if not is_allowed(update):
        return
    stats = fetch_max_token_data()
    context.bot.send_message(chat_id=update.effective_chat.id, text=stats, parse_mode="HTML")

updater = Updater(token=config["telegram_token"], use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max))

if __name__ == "__main__":
    logger.info("Running SolMadSpecBot...")
    app.run(host="0.0.0.0", port=10000)
