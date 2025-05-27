import logging
from telegram import Bot, Update
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, Dispatcher, Filters, MessageHandler
)
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from utils import (
    fetch_max_token_data,
    get_trending_coins,
    fetch_new_tokens,
    check_suspicious_activity,
    summarize_wallet_activity,
    track_position,
    classify_sentiment,
    send_target_alerts
)
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config["telegram_token"])
updater = Updater(bot=bot, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

app = Flask(__name__)

def restricted(func):
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if config["whitelist"] and update.effective_user.id not in config["whitelist"]:
            update.message.reply_text("🚫 Access denied.")
            return
        return func(update, context, *args, **kwargs)
    return wrapper

@restricted
def start(update: Update, context: CallbackContext):
    message = (
        "<b>Welcome to SolMadSpecBot!</b>\n\n"
        "Use the following commands to explore tools:\n"
        "/max – MAX token stats\n"
        "/trending – Top 5 meme coins\n"
        "/new – New Sol tokens (<12h)\n"
        "/alerts – Suspicious activity\n"
        "/wallets – Watchlist summaries\n"
        "/score – Meme sentiment score\n"
        "/pnl – Track PnL\n"
        "/help – Full command list"
    )
    update.message.reply_text(message, parse_mode="HTML")

@restricted
def max(update: Update, context: CallbackContext):
    update.message.reply_text(fetch_max_token_data(), parse_mode="HTML")

@restricted
def trending(update: Update, context: CallbackContext):
    update.message.reply_text(get_trending_coins(), parse_mode="HTML")

@restricted
def new(update: Update, context: CallbackContext):
    update.message.reply_text(fetch_new_tokens(), parse_mode="HTML")

@restricted
def alerts(update: Update, context: CallbackContext):
    update.message.reply_text(check_suspicious_activity(), parse_mode="HTML")

@restricted
def wallets(update: Update, context: CallbackContext):
    update.message.reply_text(summarize_wallet_activity(), parse_mode="HTML")

@restricted
def pnl(update: Update, context: CallbackContext):
    update.message.reply_text(track_position(), parse_mode="HTML")

@restricted
def score(update: Update, context: CallbackContext):
    update.message.reply_text(classify_sentiment(), parse_mode="HTML")

@restricted
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "<b>Command List:</b>\n"
        "/max – MAX token stats\n"
        "/trending – Top Sol meme coins\n"
        "/new – New token launches\n"
        "/alerts – Suspicious activity\n"
        "/wallets – Watchlist wallet activity\n"
        "/score – Meme sentiment\n"
        "/pnl – Profit & loss\n"
        "/help – Show this list",
        parse_mode="HTML"
    )

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("new", new))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("score", score))
dispatcher.add_handler(CommandHandler("pnl", pnl))
dispatcher.add_handler(CommandHandler("help", help_command))

scheduler = BackgroundScheduler()
scheduler.add_job(send_target_alerts, "cron", hour=9, timezone="Asia/Bangkok")
scheduler.start()

@app.route("/")
def index():
    return "SolMadSpecBot is live"

if __name__ == "__main__":
    logging.info("Running SolMadSpecBot...")
    updater.start_polling()
    app.run(host="0.0.0.0", port=10000)
