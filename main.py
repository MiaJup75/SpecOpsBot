
import logging
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher, Updater
from flask import Flask, request
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from utils import (
    fetch_max_token_data,
    get_trending_coins,
    is_allowed,
    get_new_tokens,
    check_suspicious_activity,
    format_wallet_alerts
)

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or json.load(open("config.json"))["telegram_token"]
bot = Bot(token=TOKEN)
app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher
scheduler = BackgroundScheduler(timezone=timezone("Asia/Bangkok"))

def start(update: Update, context):
    update.message.reply_text("🤖 Welcome to SolMadSpecBot!\nUse /max, /trending, /alerts, /wallets, /new")

def max(update: Update, context):
    data = fetch_max_token_data()
    if not data:
        update.message.reply_text("⚠️ MAX token data currently unavailable.")
        return
    msg = f'''
🐶 <b>MAX Token Update</b>
💰 Price: ${data["priceUsd"]}
🏛️ Market Cap: ${data["marketCap"]}
📉 Volume (24h): ${data["volume"]}
📈 FDV: ${data["fdv"]}
📊 Buys/Sells: {data["txns"]["h24"]["buys"]}/{data["txns"]["h24"]["sells"]}
👥 Holders: {data.get("holders", "N/A")}
💧 Liquidity: ${data["liquidity"]["usd"]}
📆 Launch Age: {data.get("launchAge", "N/A")}
🔗 <a href="https://dexscreener.com/solana/8fipyfvbusjpuv2wwyk8eppnk5f9dgzs8uasputwszdc">View on Dexscreener</a>
'''.strip()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='HTML')

def trending(update: Update, context):
    trending = get_trending_coins()
    if not trending:
        update.message.reply_text("No trending coins found.")
        return
    msg = "🚀 <b>Trending Solana Meme Coins</b>\n"
    for i, coin in enumerate(trending, 1):
        msg += f"{i}. {coin['symbol']} – ${coin['priceUsd']} – Vol: ${coin['volume']}\n"
    update.message.reply_text(msg.strip(), parse_mode="HTML")

def alerts(update: Update, context):
    alerts = check_suspicious_activity()
    msg = alerts if alerts else "No suspicious activity detected."
    update.message.reply_text(msg)

def wallets(update: Update, context):
    alert_summary = format_wallet_alerts()
    update.message.reply_text(alert_summary or "No wallet alerts at this time.")

def new(update: Update, context):
    tokens = get_new_tokens()
    msg = tokens if tokens else "No new token launches detected."
    update.message.reply_text(msg)

def send_daily_report():
    for user_id in json.load(open("config.json"))["whitelist"]:
        bot.send_message(chat_id=user_id, text="<b>📊 Daily Report (placeholder)</b>", parse_mode="HTML")

@app.route("/hook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "✅ SolMadSpecBot is running."

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("new", new))

scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

if __name__ == "__main__":
    bot.set_webhook(url="https://solmad-spec-bot.onrender.com/hook")
    app.run(host="0.0.0.0", port=10000)
