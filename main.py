import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from utils import (
    get_token_stats,
    fetch_trending_tokens,
    fetch_new_tokens,
    check_suspicious_activity,
    track_position,
    score_sentiment,
    detect_stealth_launches,
    analyze_wallet_clusters,
    send_wallet_activity,
)
from config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config["telegram_token"]
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=1)

# === COMMANDS ===

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("📈 MAX Update", callback_data='max')],
        [InlineKeyboardButton("🚀 Trending Coins", callback_data='trending')],
        [InlineKeyboardButton("🆕 New Tokens", callback_data='new')],
        [InlineKeyboardButton("⚠️ Alerts", callback_data='alerts')],
        [InlineKeyboardButton("📊 Wallets", callback_data='wallets')],
        [InlineKeyboardButton("📉 PnL Tracker", callback_data='pnl')],
        [InlineKeyboardButton("🧠 Sentiment", callback_data='sentiment')],
        [InlineKeyboardButton("🕵️ Stealth Tokens", callback_data='stealth')],
        [InlineKeyboardButton("🔍 Mirror Wallets", callback_data='mirror')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "<b>Welcome to SolMadSpecBot!</b>\nChoose an option or use /help for commands.",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )

def help_command(update, context):
    update.message.reply_text(
        "<b>📘 Available Commands</b>\n"
        "/max - MAX token update\n"
        "/trending - Top Solana meme coins\n"
        "/new - New token launches\n"
        "/alerts - Whale/dev/liquidity alerts\n"
        "/wallets - Tracked wallet activity\n"
        "/pnl - PnL position tracking\n"
        "/sentiment - Meme sentiment meter\n"
        "/stealth - Stealth token radar\n"
        "/mirror - Mirror wallet detection\n",
        parse_mode="HTML",
    )

def max(update, context):
    result = get_token_stats(config["max_token"])
    update.message.reply_text(result["message"], parse_mode="HTML")

def trending(update, context):
    result = fetch_trending_tokens()
    update.message.reply_text(result, parse_mode="HTML")

def new(update, context):
    result = fetch_new_tokens()
    update.message.reply_text(result, parse_mode="HTML")

def alerts(update, context):
    result = check_suspicious_activity()
    update.message.reply_text(result, parse_mode="HTML")

def wallets(update, context):
    result = send_wallet_activity()
    update.message.reply_text(result, parse_mode="HTML")

def pnl(update, context):
    result = track_position()
    update.message.reply_text(result, parse_mode="HTML")

def sentiment(update, context):
    result = score_sentiment()
    update.message.reply_text(result, parse_mode="HTML")

def stealth(update, context):
    result = detect_stealth_launches()
    update.message.reply_text(result, parse_mode="HTML")

def mirror(update, context):
    result = analyze_wallet_clusters()
    update.message.reply_text(result, parse_mode="HTML")

def button_handler(update, context):
    query = update.callback_query
    data = query.data

    query.answer()
    command_map = {
        "max": get_token_stats(config["max_token"])["message"],
        "trending": fetch_trending_tokens(),
        "new": fetch_new_tokens(),
        "alerts": check_suspicious_activity(),
        "wallets": send_wallet_activity(),
        "pnl": track_position(),
        "sentiment": score_sentiment(),
        "stealth": detect_stealth_launches(),
        "mirror": analyze_wallet_clusters(),
    }

    query.edit_message_text(text=command_map.get(data, "Unknown"), parse_mode="HTML")

# === DAILY SUMMARY ===

def send_daily_report():
    message = f"""
<b>📊 Daily Summary</b>

{get_token_stats(config["max_token"])["message"]}

{fetch_trending_tokens()}

{fetch_new_tokens()}

{check_suspicious_activity()}

{send_wallet_activity()}

{track_position()}

{score_sentiment()}

{detect_stealth_launches()}

{analyze_wallet_clusters()}
    """
    for user_id in config.get("whitelist", []):
        try:
            bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Failed to send summary to {user_id}: {e}")

# === ROUTES ===

@app.route("/")
def index():
    return "SolMadSpecBot is live!"

@app.route("/hook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return "OK"

# === INIT ===

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("new", new))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("pnl", pnl))
dispatcher.add_handler(CommandHandler("sentiment", sentiment))
dispatcher.add_handler(CommandHandler("stealth", stealth))
dispatcher.add_handler(CommandHandler("mirror", mirror))
dispatcher.add_handler(CommandHandler("debug", help_command))
dispatcher.add_handler(CommandHandler("report", lambda u, c: send_daily_report()))

from telegram.ext import CallbackQueryHandler
dispatcher.add_handler(CallbackQueryHandler(button_handler))

if __name__ == "__main__":
    logger.info("Running SolMadSpecBot...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_report, "cron", hour=9, timezone="Asia/Bangkok")
    scheduler.start()
    app.run(host="0.0.0.0", port=10000)
