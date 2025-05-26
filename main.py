import json
import logging
from telegram import Bot, Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Dispatcher, CallbackContext
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from utils import fetch_max_token_data, is_allowed, get_trending_coins

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=1)

# Commands
def start_command(update: Update, context: CallbackContext):
    welcome_text = (
        "<b>🤖 Welcome to SolMadSpecBot!</b>\n"
        "Use /max to check MAX token status.\n"
        "Use /trending to view top Solana meme coins."
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text, parse_mode=ParseMode.HTML)

def max_command(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        return
    try:
        price, market_cap, volume, fdv = fetch_max_token_data()
        message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${price:.8f}
🏦 Market Cap: ${market_cap:,.0f}
📈 Volume (24h): ${volume:,.0f}
🏛️ FDV: ${fdv:,.0f}"""
    except Exception as e:
        message = f"⚠️ Error fetching data: {e}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def trending_command(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        return
    try:
        coins = get_trending_coins()
        message = "<b>🚀 Trending Solana Meme Coins</b>\n"
        for i, coin in enumerate(coins[:5], 1):
            message += f"{i}. {coin['symbol']} – ${coin['priceUsd']:.8f} – Vol: ${coin['volume']:,}\n"
    except Exception as e:
        message = f"⚠️ Error fetching trending coins: {e}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

# Dispatcher handlers
dispatcher.add_handler(CommandHandler("start", start_command))
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("trending", trending_command))

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# Daily job (placeholder)
def send_daily_report():
    try:
        message = "<b>📊 Daily Report (placeholder)</b>"
        for user_id in config["whitelist"]:
            bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Daily report error: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=9, timezone="Asia/Bangkok")
scheduler.start()

# Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)