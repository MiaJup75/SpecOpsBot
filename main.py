import logging
from telegram import Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from config import config
from utils import (
    fetch_max_token_data,
    fetch_trending_tokens,
    fetch_new_tokens,
    check_suspicious_activity,
    summarize_wallet_activity,
    send_target_alerts,
    send_wallet_activity,
    track_position,
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = Bot(token=config["telegram_token"])
scheduler = BackgroundScheduler()


@app.route("/")
def home():
    return "SolMadSpecBot is running!"


def start(update: Update, context: CallbackContext):
    welcome_message = (
        "<b>Welcome to SolMadSpecBot!</b>\n\n"
        "🤖 I scan Solana meme coins and alert you on:\n"
        "• New launches under 12h\n"
        "• Trending coins by volume\n"
        "• Suspicious whale or LP actions\n"
        "• MAX token metrics\n"
        "• Wallet activity summaries\n\n"
        "📌 Type /help to view commands!"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_message,
        parse_mode=ParseMode.HTML,
    )


def help_command(update: Update, context: CallbackContext):
    help_text = (
        "<b>📖 SolMadSpecBot Commands</b>\n"
        "/start - Show welcome message\n"
        "/max - Show MAX token update\n"
        "/wallets - Show wallet activity\n"
        "/trending - Show trending Solana meme coins\n"
        "/new - Show new tokens (<12h old)\n"
        "/alerts - Suspicious dev/whale/LP activity\n"
        "/targets - Show target price alerts\n"
        "/debug - Run all features in test mode"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_text,
        parse_mode=ParseMode.HTML,
    )


def max_command(update: Update, context: CallbackContext):
    message = fetch_max_token_data()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


def trending_command(update: Update, context: CallbackContext):
    message = fetch_trending_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)


def new_command(update: Update, context: CallbackContext):
    message = fetch_new_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)


def alerts_command(update: Update, context: CallbackContext):
    message = check_suspicious_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)


def wallets_command(update: Update, context: CallbackContext):
    message = send_wallet_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)


def targets_command(update: Update, context: CallbackContext):
    message = send_target_alerts()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)


def debug_command(update: Update, context: CallbackContext):
    debug_output = (
        fetch_max_token_data()
        + "\n\n"
        + fetch_trending_tokens()
        + "\n\n"
        + fetch_new_tokens()
        + "\n\n"
        + check_suspicious_activity()
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=debug_output, parse_mode=ParseMode.HTML)


def send_daily_report():
    try:
        report = (
            fetch_max_token_data()
            + "\n\n"
            + fetch_trending_tokens()
            + "\n\n"
            + fetch_new_tokens()
            + "\n\n"
            + check_suspicious_activity()
            + "\n\n"
            + summarize_wallet_activity()
        )
        for uid in config["whitelist"]:
            bot.send_message(chat_id=uid, text=report, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error sending daily report: {e}")


def main():
    updater = Updater(token=config["telegram_token"], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("max", max_command))
    dispatcher.add_handler(CommandHandler("wallets", wallets_command))
    dispatcher.add_handler(CommandHandler("trending", trending_command))
    dispatcher.add_handler(CommandHandler("new", new_command))
    dispatcher.add_handler(CommandHandler("alerts", alerts_command))
    dispatcher.add_handler(CommandHandler("targets", targets_command))
    dispatcher.add_handler(CommandHandler("debug", debug_command))

    updater.start_polling()
    scheduler.add_job(send_daily_report, "cron", hour=9, timezone="Asia/Bangkok")
    scheduler.start()


if __name__ == "__main__":
    logger.info("Running SolMadSpecBot...")
    main()
