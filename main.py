import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from config import config
from utils import (
    fetch_max_token_data,
    is_allowed,
    send_target_alerts,
    format_number,
    format_launch_time,
    send_wallet_activity,
    send_trending_coins,
    fetch_new_tokens,
    summarize_wallet_activity,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = Bot(token=config["telegram_token"])
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

def start(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        return
    message = (
        "<b>Welcome to SolMadSpecBot!</b>\n\n"
        "📈 <b>Available Commands:</b>\n"
        "/max – MAX token update\n"
        "/wallets – Watch wallet activity\n"
        "/trending – Top Solana meme coins\n"
        "/new – New tokens launched (<12h)\n"
        "/alerts – Suspicious activity monitor\n"
        "/score – Post-launch token score\n"
        "/pnl – Track PnL & cost basis\n"
        "/suggest – Get buy/sell prompt\n"
        "/start – Show this menu again"
    )
    keyboard = [
        [InlineKeyboardButton("📈 Trending", callback_data="trending")],
        [InlineKeyboardButton("🐶 MAX Update", callback_data="max")],
        [InlineKeyboardButton("🔍 New Tokens", callback_data="new")],
    ]
    update.message.reply_text(
        message, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )

def max_token(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        return
    data = fetch_max_token_data()
    message = (
        f"🐶 <b>MAX Token Update</b>\n"
        f"💰 Price: ${format_number(data['priceUsd'])}\n"
        f"🏛️ Market Cap: ${format_number(data['marketCap'])}\n"
        f"📉 Volume (24h): ${format_number(data['volume'])}\n"
        f"🏦 FDV: ${format_number(data['fdv'])}\n"
        f"📊 Buys: {data['txns'].get('buys', 0)} | Sells: {data['txns'].get('sells', 0)}\n"
        f"💧 Liquidity: ${format_number(data['liquidity'])}\n"
        f"📈 24H Change: {format_number(data['priceChange'])}%\n"
        f"🔢 Holders: {data['holders']}\n"
        f"🕐 Launch Time: {format_launch_time(data['timestamp'])}\n"
        f"🔗 <a href='{data['url']}'>View on Dexscreener</a>"
    )
    update.message.reply_text(message, parse_mode="HTML")

def trending(update: Update, context: CallbackContext):
    if is_allowed(update.effective_user.id):
        send_trending_coins(update, context)

def new_tokens(update: Update, context: CallbackContext):
    if is_allowed(update.effective_user.id):
        fetch_new_tokens(update, context)

def alerts(update: Update, context: CallbackContext):
    if is_allowed(update.effective_user.id):
        summarize_wallet_activity(update, context)

def wallets(update: Update, context: CallbackContext):
    if is_allowed(update.effective_user.id):
        send_wallet_activity(update, context)

def pnl(update: Update, context: CallbackContext):
    if is_allowed(update.effective_user.id):
        update.message.reply_text("📊 PnL tracking coming soon (Beta)")

def suggest(update: Update, context: CallbackContext):
    if is_allowed(update.effective_user.id):
        update.message.reply_text("🧠 AI Buy/Sell Suggestion (Coming Soon!)")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max_token))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("new", new_tokens))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("pnl", pnl))
dispatcher.add_handler(CommandHandler("suggest", suggest))

@app.route("/", methods=["GET", "HEAD"])
def index():
    return "SolMadSpecBot is running"

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

def send_daily_report():
    try:
        message = "<b>📊 Daily Report</b>\nStill under construction."
        bot.send_message(chat_id=config["whitelist"][0], text=message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error sending daily report: {e}")

scheduler = BackgroundScheduler(timezone=timezone("Asia/Bangkok"))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

if __name__ == "__main__":
    logger.info("Running SolMadSpecBot...")
    app.run(host="0.0.0.0", port=10000)
