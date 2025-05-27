import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from flask import Flask
from utils import (
    fetch_max_token_data,
    get_trending_coins,
    fetch_new_tokens,
    check_suspicious_activity,
    track_position,
    send_target_alerts,
    analyze_sentiment,
    detect_stealth_launches,
    ai_trade_prompt,
    detect_botnets,
    track_mirror_wallets,
    summarize_wallet_activity,
)
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config["telegram_token"]
ALLOWED_USERS = config["whitelist"]

app = Flask(__name__)
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))


def restricted(func):
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id not in ALLOWED_USERS:
            update.message.reply_text("Unauthorized")
            return
        return func(update, context, *args, **kwargs)
    return wrapper


@restricted
def start(update: Update, context: CallbackContext):
    message = """<b>Welcome to SolMadSpecBot!</b>

Available Commands:
/start – Show welcome message
/help – Show command list
/max – MAX token stats
/trending – Top Sol meme coins
/new – Fresh launches (<12h)
/alerts – Suspicious activity
/wallets – Tracked wallet activity
/ai – Get AI trading prompt"""
    update.message.reply_text(message, parse_mode="HTML")


@restricted
def help_command(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📈 Trending", callback_data='trending')],
        [InlineKeyboardButton("🆕 New Launches", callback_data='new')],
        [InlineKeyboardButton("🚨 Alerts", callback_data='alerts')],
        [InlineKeyboardButton("🐶 MAX Token", callback_data='max')],
        [InlineKeyboardButton("📊 Wallet Activity", callback_data='wallets')],
        [InlineKeyboardButton("🤖 AI Prompt", callback_data='ai')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a command:", reply_markup=reply_markup)


def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    command = query.data
    fake_update = Update(update.update_id, message=query.message)
    if command == "trending":
        get_trending_coins(fake_update, context)
    elif command == "new":
        fetch_new_tokens(fake_update, context)
    elif command == "alerts":
        check_suspicious_activity(fake_update, context)
    elif command == "max":
        fetch_max_token_data(fake_update, context)
    elif command == "wallets":
        summarize_wallet_activity(fake_update, context)
    elif command == "ai":
        ai_trade_prompt(fake_update, context)


def send_daily_report():
    logging.info("⏰ Sending daily summary...")
    # Add reporting logic here


def main():
    logging.info("Running SolMadSpecBot...")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("max", fetch_max_token_data))
    dp.add_handler(CommandHandler("trending", get_trending_coins))
    dp.add_handler(CommandHandler("new", fetch_new_tokens))
    dp.add_handler(CommandHandler("alerts", check_suspicious_activity))
    dp.add_handler(CommandHandler("wallets", summarize_wallet_activity))
    dp.add_handler(CommandHandler("ai", ai_trade_prompt))
    dp.add_handler(CallbackQueryHandler(handle_button))

    scheduler.add_job(send_daily_report, "cron", hour=9)
    scheduler.start()

    updater.start_polling()
    app.run(host="0.0.0.0", port=10000)


if __name__ == "__main__":
    main()
