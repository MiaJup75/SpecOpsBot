import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import pytz
from utils import fetch_max_token_data, is_allowed, get_trending_coins

app = Flask(__name__)

with open("config.json") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=1, use_context=True)
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))

# --- Commands ---

def start(update: Update, context: CallbackContext):
    message = (
        "<b>Welcome to SolMadSpecBot!</b>

"
        "Use the following commands:
"
        "/max - 📈 View MAX token data
"
        "/trending - 🚀 Top 5 trending SOL meme coins
"
        "/wallets - 👛 Wallet tracking data
"
        "/alerts - ⚠️ Suspicious activity alerts
"
        "/new - 🆕 New token launches"
    )
    update.message.reply_text(message, parse_mode="HTML")

def max(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if not is_allowed(user_id):
        return update.message.reply_text("⛔ Access denied.")

    data = fetch_max_token_data()
    if not data:
        return update.message.reply_text("⚠️ Unable to fetch MAX token data.")

    message = (
        "<b>MAX Token Update</b>

"
        f"💰 Price: ${data['price_usd']}
"
        f"📊 24h Volume: ${data['volume_usd']}
"
        f"💧 Liquidity: ${data['liquidity_usd']}
"
        f"📈 Market Cap: ${data['market_cap']}
"
        f"📉 24h Change: {data['price_change']}%

"
        f"🔗 <a href='{data['url']}'>View on Dexscreener</a>"
    )
    update.message.reply_text(message, parse_mode="HTML")

def trending(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if not is_allowed(user_id):
        return update.message.reply_text("⛔ Access denied.")

    trending_coins = get_trending_coins()
    if not trending_coins:
        return update.message.reply_text("⚠️ Unable to fetch trending coins.")

    message = "<b>🔥 Top 5 Trending Solana Meme Coins</b>

"
    for i, coin in enumerate(trending_coins, 1):
        message += f"{i}. {coin['name']} (${coin['price']})
🔗 {coin['url']}

"

    update.message.reply_text(message, parse_mode="HTML")

def send_daily_report():
    message = "<b>📊 Daily Report (placeholder)</b>
Coming soon..."
    for user_id in config["whitelist"]:
        try:
            bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Error sending to {user_id}: {e}")

# --- Register Handlers ---

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))

scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("🔄 Starting webhook server...")
    bot.set_webhook(url="https://solmad-spec-bot.onrender.com/hook")
    app.run(host="0.0.0.0", port=10000)