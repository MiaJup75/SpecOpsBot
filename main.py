import logging
from flask import Flask, request
from telegram import Bot, Update, BotCommand
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from utils import (
    fetch_max_token_data,
    fetch_new_tokens,
    check_suspicious_activity,
    fetch_trending_tokens,
    summarize_wallet_activity,
    track_position,
    get_pnl,
    set_target_price,
    check_target_price,
    suggest_gas_timing,
    sentiment_score
)
from config import config
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config["telegram_token"]
bot = Bot(token=TOKEN)

app = Flask(__name__)
dp = Dispatcher(bot, None, workers=1, use_context=True)

# --- Command Handlers ---

def start(update: Update, context: CallbackContext):
    message = """<b>Welcome to SolMadSpecBot!</b>
🤖 Your crypto companion on Solana

Available commands:
/max – MAX Token Stats
/trending – Top SOL meme coins
/new – Freshly launched tokens
/alerts – Suspicious token activity
/wallets – Top wallet movement
/track – Track your buy position
/pnl – Check your token profit/loss
/settarget – Set a sell alert
/gas – Best timing to buy/sell
/sentiment – Meme market mood
/stealths – Stealth launch radar"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML"
    )

dp.add_handler(CommandHandler("start", start))

def max(update: Update, context: CallbackContext):
    message = fetch_max_token_data()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML"
    )

dp.add_handler(CommandHandler("max", max))

def trending(update: Update, context: CallbackContext):
    message = fetch_trending_tokens()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML"
    )

dp.add_handler(CommandHandler("trending", trending))

def new(update: Update, context: CallbackContext):
    message = fetch_new_tokens()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML"
    )

dp.add_handler(CommandHandler("new", new))

def alerts(update: Update, context: CallbackContext):
    message = check_suspicious_activity()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML"
    )

dp.add_handler(CommandHandler("alerts", alerts))

def wallets(update: Update, context: CallbackContext):
    message = summarize_wallet_activity()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML"
    )

dp.add_handler(CommandHandler("wallets", wallets))

def track(update: Update, context: CallbackContext):
    try:
        token, amount, price = context.args
        track_position(update.effective_user.id, token.upper(), float(amount), float(price))
        update.message.reply_text(f"Tracking {amount} {token.upper()} at ${price}")
    except:
        update.message.reply_text("Usage: /track [TOKEN] [AMOUNT] [BUY_PRICE]")

dp.add_handler(CommandHandler("track", track))

def pnl(update: Update, context: CallbackContext):
    try:
        token, current_price = context.args
        message = get_pnl(update.effective_user.id, token.upper(), float(current_price))
        update.message.reply_text(message)
    except:
        update.message.reply_text("Usage: /pnl [TOKEN] [CURRENT_PRICE]")

dp.add_handler(CommandHandler("pnl", pnl))

def set_target(update: Update, context: CallbackContext):
    try:
        token, price = context.args
        set_target_price(update.effective_user.id, token.upper(), float(price))
        update.message.reply_text(f"🎯 Target set for {token.upper()} at ${price}")
    except:
        update.message.reply_text("Usage: /settarget [TOKEN] [TARGET_PRICE]")

dp.add_handler(CommandHandler("settarget", set_target))

def gas(update: Update, context: CallbackContext):
    update.message.reply_text(suggest_gas_timing())

dp.add_handler(CommandHandler("gas", gas))

def sentiment(update: Update, context: CallbackContext):
    update.message.reply_text(sentiment_score())

dp.add_handler(CommandHandler("sentiment", sentiment))

def stealths(update: Update, context: CallbackContext):
    update.message.reply_text("🕵️‍♂️ No recent stealth launches detected.\n(Live scanning coming soon.)")

dp.add_handler(CommandHandler("stealths", stealths))

# --- Daily Scheduler ---

def send_daily_report():
    for user_id in config["whitelist"]:
        try:
            bot.send_message(
                chat_id=user_id,
                text="<b>📊 Daily Report (placeholder)</b>",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Failed to send daily report to {user_id}: {e}")

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Bangkok"))
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

# --- Webhook Endpoint ---

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return "ok"

@app.route("/", methods=["GET", "HEAD"])
def index():
    return "SolMadSpecBot is live."

# --- Bot Commands for Telegram Menu ---

bot.set_my_commands([
    BotCommand("start", "Start the bot"),
    BotCommand("max", "MAX Token Stats"),
    BotCommand("trending", "Top SOL meme coins"),
    BotCommand("new", "New tokens <24h"),
    BotCommand("alerts", "Suspicious token activity"),
    BotCommand("wallets", "Wallet Tracker Summary"),
    BotCommand("track", "Track token buy position"),
    BotCommand("pnl", "Check your PnL"),
    BotCommand("settarget", "Set a sell alert"),
    BotCommand("gas", "Gas-efficient timing"),
    BotCommand("sentiment", "Meme market sentiment"),
    BotCommand("stealths", "Stealth launch radar")
])

# --- Run the bot ---

if __name__ == "__main__":
    logging.info("Running SolMadSpecBot...")
    app.run(host="0.0.0.0", port=10000)
