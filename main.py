import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)
from config import config
from utils import (
    fetch_max_token_data,
    fetch_trending_tokens,
    fetch_new_tokens,
    check_suspicious_activity,
    summarize_wallet_activity,
    track_position,
    fetch_pnl,
    fetch_sentiment_score,
    detect_stealth_launches,
    check_target_alerts,
    check_mirror_wallets,
    send_daily_report,
)

from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from flask import Flask

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app (to keep Render.com service alive)
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is live!"

# Telegram bot setup
updater = Updater(token=config["telegram_token"], use_context=True)
dispatcher = updater.dispatcher

# --- Command Handlers ---

def start(update, context: CallbackContext):
    welcome = (
        "<b>Welcome to SolMadSpecBot!</b>\n"
        "🤖 I scan Solana meme coins and alert you on:\n"
        "• New launches under 12h\n"
        "• Trending coins by volume\n"
        "• Suspicious whale or LP actions\n"
        "• MAX token metrics\n"
        "• Wallet activity summaries\n\n"
        "📌 Type /help to view commands!"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome, parse_mode=ParseMode.HTML)

def help_command(update, context: CallbackContext):
    help_text = (
        "<b>Here’s what I can do:</b>\n"
        "/max – MAX token stats\n"
        "/trending – Top 5 Sol meme coins\n"
        "/new – New token launches\n"
        "/alerts – Suspicious activity\n"
        "/wallets – Watchlist summaries\n"
        "/pnl – PnL & break-even\n"
        "/sentiment – Emoji sentiment meter\n"
        "/targetalerts – Sell zone triggers\n"
        "/stealthlaunches – Hidden tokens\n"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode=ParseMode.HTML)

def max_command(update, context: CallbackContext):
    msg = fetch_max_token_data()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def trending_command(update, context: CallbackContext):
    msg = fetch_trending_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def new_command(update, context: CallbackContext):
    msg = fetch_new_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def alerts_command(update, context: CallbackContext):
    msg = check_suspicious_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def wallets_command(update, context: CallbackContext):
    msg = summarize_wallet_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def pnl_command(update, context: CallbackContext):
    msg = fetch_pnl()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def sentiment_command(update, context: CallbackContext):
    msg = fetch_sentiment_score()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def target_alerts_command(update, context: CallbackContext):
    msg = check_target_alerts()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def stealth_command(update, context: CallbackContext):
    msg = detect_stealth_launches()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

def mirror_command(update, context: CallbackContext):
    msg = check_mirror_wallets()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=ParseMode.HTML)

# --- Inline Buttons Example Handler ---

def inline_button_handler(update, context: CallbackContext):
    query = update.callback_query
    if query.data == "max_price":
        msg = fetch_max_token_data()
        context.bot.send_message(chat_id=query.message.chat_id, text=msg, parse_mode=ParseMode.HTML)

# --- Command Mapping ---

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("trending", trending_command))
dispatcher.add_handler(CommandHandler("new", new_command))
dispatcher.add_handler(CommandHandler("alerts", alerts_command))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("pnl", pnl_command))
dispatcher.add_handler(CommandHandler("sentiment", sentiment_command))
dispatcher.add_handler(CommandHandler("targetalerts", target_alerts_command))
dispatcher.add_handler(CommandHandler("stealthlaunches", stealth_command))
dispatcher.add_handler(CommandHandler("mirrorwallets", mirror_command))
dispatcher.add_handler(CallbackQueryHandler(inline_button_handler))

# --- Daily Report Scheduler ---

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=9, timezone=pytz.timezone("Asia/Bangkok"))
scheduler.start()

# --- Run Bot ---

if __name__ == "__main__":
    logger.info("Running SolMadSpecBot...")
    updater.start_polling()
    updater.idle()
