
import logging
import json
import pytz
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from utils import fetch_max_token_data, is_allowed, fetch_trending_coins

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dispatcher setup
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

# Welcome message with commands
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in WHITELIST:
        return
    keyboard = [
        [InlineKeyboardButton("/max", callback_data='max')],
        [InlineKeyboardButton("/wallets", callback_data='wallets')],
        [InlineKeyboardButton("/trending", callback_data='trending')],
        [InlineKeyboardButton("/new", callback_data='new')],
        [InlineKeyboardButton("/alerts", callback_data='alerts')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = (
        "<b>Welcome to SolMadSpecBot!</b>

"
        "Choose a command below to begin tracking Solana meme coins:
"
    )
    update.message.reply_text(message, parse_mode='HTML', reply_markup=reply_markup)

# Command: /max
def max(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if not is_allowed(user_id):
        return
    data = fetch_max_token_data()
    if not data:
        update.message.reply_text("❌ Unable to fetch MAX token data.")
        return
    message = f"""🐶 <b>MAX Token Update</b>
Price: ${data['priceUsd']}
Volume (24h): ${data['volume']}
Liquidity: ${data['liquidity']}
FDV: ${data['fdv']}
Market Cap: ${data['marketCap']}
Buys (24h): {data['buys']} | Sells (24h): {data['sells']}
"""
    update.message.reply_text(message, parse_mode='HTML')

# Command: /trending
def trending(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if not is_allowed(user_id):
        return
    trending_data = fetch_trending_coins()
    if not trending_data:
        update.message.reply_text("❌ Unable to fetch trending data.")
        return
    message = "<b>🔥 Top 5 Trending Solana Meme Coins</b>

"
    for token in trending_data:
        message += f"{token}\n"
    update.message.reply_text(message, parse_mode='HTML')

# Scheduler daily 9AM Bangkok
def send_daily_report():
    for user_id in WHITELIST:
        try:
            message = "<b>📊 Daily Report (placeholder)</b>"
            bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Failed to send daily report to {user_id}: {e}")

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Bangkok'))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

# Add command handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))

# Flask route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "SolMadSpecBot is running."

if __name__ == "__main__":
    logger.info("🔄 Starting webhook server...")
    app.run(host="0.0.0.0", port=10000)
