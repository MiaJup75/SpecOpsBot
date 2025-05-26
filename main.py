# main.py (simplified structure placeholder)
from utils import fetch_max_token_data, is_allowed
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
import json, logging

app = Flask(__name__)
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("📊 View MAX", callback_data='max')]]
    update.message.reply_text(
        "Welcome to SolMadSpecBot!
Use /max to get token stats.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def max_handler(update: Update, context: CallbackContext):
    stats = fetch_max_token_data()
    update.message.reply_text(stats, parse_mode="HTML")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_handler))

if __name__ == "__main__":
    app.run(port=10000)
