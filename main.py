import os
import json
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")
WHITELIST = ["7623873892"]
MAX_TOKEN = "EQbLvkkT8htw9uiC6AG4wwHEsmV4zHQkTNyF6yJDpump"

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)

logging.basicConfig(level=logging.INFO)

def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        update.message.reply_text("⛔ You’re not authorized to use this bot.")
        return
    update.message.reply_text("🤖 Welcome to SolMadSpecBot!\nTracking wallets, MAX token & meme coins daily...")

def max_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        update.message.reply_text("⛔ You’re not authorized to use this bot.")
        return
    try:
        url = f"https://multichain-api.birdeye.so/solana/overview/token_stats?address={MAX_TOKEN}&time_frame=24h"
        headers = {"X-API-KEY": "public"}
        res = requests.get(url, headers=headers).json()
        data = res.get("data", {})
        price = float(data.get("price", 0))
        market_cap = round(price * 1_000_000_000, 2)
        message = f"🌐 MAX Token Info:\nPrice: ${price:.9f}\nMarket Cap: ${market_cap:,.2f}"
    except Exception as e:
        message = f"⚠️ Error fetching MAX data: {e}"
    update.message.reply_text(message)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_command))

@app.route('/hook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route('/')
def index():
    return 'Bot is running.'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)