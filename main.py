import logging
from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler, Dispatcher, Updater
from flask import Flask, request
import json
from utils import fetch_max_token_data, get_trending_coins, is_allowed, get_new_tokens, get_alerts, get_wallet_activity
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

with open("config.json") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
bot = Bot(token=TOKEN)
app = Flask(__name__)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Commands
def max_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    price, market_cap, volume, fdv = fetch_max_token_data()
    message = f"""🐶 <b>MAX Token Update</b>
💰 Price: ${price:.8f}
🏛️ Market Cap: ${market_cap:,.0f}
📉 Volume (24h): ${volume:,.0f}
🏦 FDV: ${fdv:,.0f}"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def trending_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    trending = get_trending_coins()
    message = "🚀 <b>Trending Solana Meme Coins</b>\n"
    for i, coin in enumerate(trending, 1):
        message += f"{i}. {coin['name']} – ${coin['price']} – Vol: ${coin['volume']:,}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def new_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    tokens = get_new_tokens()
    message = "🆕 <b>New Meme Coins (last 12h)</b>\n"
    if not tokens:
        message += "No new tokens found."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def alerts_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    alerts = get_alerts()
    message = "⚠️ <b>Suspicious Activity Alerts</b>\n"
    if not alerts:
        message += "No alerts found."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def wallets_command(update: Update, context):
    if not is_allowed(update.effective_user.id):
        return
    activity = get_wallet_activity()
    message = "👛 <b>Tracked Wallet Activity</b>\n"
    if not activity:
        message += "No recent activity."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

def send_daily_report():
    message = "<b>📊 Daily Report (placeholder)</b>\nSummary stats here."
    for user_id in config["whitelist"]:
        bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)

# Register commands
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("trending", trending_command))
dispatcher.add_handler(CommandHandler("new", new_command))
dispatcher.add_handler(CommandHandler("alerts", alerts_command))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))

# Scheduler
scheduler = BackgroundScheduler(timezone=timezone("Asia/Bangkok"))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

# Pinned welcome message
for user_id in config["whitelist"]:
    bot.send_message(
        chat_id=user_id,
        text=(
            "<b>🤖 Welcome to SolMadSpecBot!</b>\n"
            "Use /max to check MAX token status.\n"
            "Use /trending to view top Solana meme coins.\n"
            "Use /new for new token launches.\n"
            "Use /alerts to view dev/LP alerts.\n"
            "Use /wallets to monitor key wallets."
        ),
        parse_mode=ParseMode.HTML
    )

logging.basicConfig(level=logging.INFO)
print("🔄 Starting webhook server...")
app.run(host="0.0.0.0", port=10000)