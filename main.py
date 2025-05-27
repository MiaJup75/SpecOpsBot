import logging
import pytz
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
from utils import (
    fetch_max_token_data,
    fetch_trending_tokens,
    fetch_new_tokens,
    summarize_wallet_activity,
    check_suspicious_activity,
    track_position,
    send_target_alerts,
    suggest_low_mev_timing,
    analyze_sentiment,
    detect_stealth_launches,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config["telegram_token"]
WHITELIST = config.get("whitelist", [])

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=1, use_context=True)


def is_allowed(user_id):
    return str(user_id) in WHITELIST


def start(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "<b>Welcome to SolMadSpecBot!</b>\n\n"
            "Available commands:\n"
            "/max – View MAX token update\n"
            "/trending – Top 5 trending SOL meme coins\n"
            "/new – Tokens launched <24h\n"
            "/alerts – Suspicious activity alerts\n"
            "/wallets – Watched wallet activity\n"
            "/pnl – Track your position PnL\n"
            "/target – Trigger alerts when price hits sell zone\n"
            "/mev – Get low MEV timing suggestions\n"
            "/sentiment – Meme sentiment score\n"
            "/stealth – Detect stealth launches\n"
        ),
        parse_mode="HTML"
    )


def handle_max(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = fetch_max_token_data()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_trending(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = fetch_trending_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_new(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = fetch_new_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_alerts(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = check_suspicious_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_wallets(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = summarize_wallet_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_pnl(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = track_position()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_target(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = send_target_alerts()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_mev(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = suggest_low_mev_timing()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_sentiment(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = analyze_sentiment()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


def handle_stealth(update, context):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    message = detect_stealth_launches()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", handle_max))
dispatcher.add_handler(CommandHandler("trending", handle_trending))
dispatcher.add_handler(CommandHandler("new", handle_new))
dispatcher.add_handler(CommandHandler("alerts", handle_alerts))
dispatcher.add_handler(CommandHandler("wallets", handle_wallets))
dispatcher.add_handler(CommandHandler("pnl", handle_pnl))
dispatcher.add_handler(CommandHandler("target", handle_target))
dispatcher.add_handler(CommandHandler("mev", handle_mev))
dispatcher.add_handler(CommandHandler("sentiment", handle_sentiment))
dispatcher.add_handler(CommandHandler("stealth", handle_stealth))


@app.route("/", methods=["GET", "HEAD"])
def index():
    return "SolMadSpecBot is running!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"


def send_daily_report():
    for user_id in WHITELIST:
        try:
            bot.send_message(chat_id=user_id, text="<b>📊 Daily Report (placeholder)</b>", parse_mode="HTML")
        except Exception as e:
            logging.error(f"Error sending daily report to {user_id}: {e}")


if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
    scheduler.add_job(send_daily_report, "cron", hour=9)
    scheduler.start()
    logging.info("Running SolMadSpecBot...")
    app.run(host="0.0.0.0", port=10000)
