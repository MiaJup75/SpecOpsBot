import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    Dispatcher,
    Updater,
)
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
from utils import (
    fetch_max_token_data,
    fetch_trending_tokens,
    fetch_new_tokens,
    check_suspicious_activity,
    summarize_wallet_activity,
    track_position,
    analyze_sentiment,
    find_stealth_launches,
    classify_narratives,
    detect_mirror_wallets,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = Bot(token=config["telegram_token"])
updater = Updater(bot=bot, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

scheduler = BackgroundScheduler()
scheduler.start()

WHITELIST = config.get("whitelist", [])
MAX_TOKEN_ADDRESS = config["max_token"]
WALLETS = config["wallets"]

def restricted(func):
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if user_id not in WHITELIST:
            update.message.reply_text("🚫 Access denied.")
            return
        return func(update, context, *args, **kwargs)
    return wrapper

@restricted
def start(update: Update, context: CallbackContext):
    message = (
        "<b>Welcome to SolMadSpecBot!</b>\n\n"
        "🤖 I scan Solana meme coins and alert you on:\n"
        "• New launches under &lt;12h\n"
        "• Trending coins by volume\n"
        "• Suspicious whale or LP actions\n"
        "• MAX token metrics\n"
        "• Wallet activity summaries\n\n"
        "📌 Type /help to view commands!"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def help_command(update: Update, context: CallbackContext):
    message = (
        "<b>Here's what I can do:</b>\n\n"
        "/max – MAX token stats\n"
        "/trending – Top 5 Sol meme coins\n"
        "/new – New token launches (&lt;12h)\n"
        "/alerts – Suspicious activity\n"
        "/wallets – Watchlist summaries\n"
        "/pnl – PnL & break-even\n"
        "/targetalerts – Targeted whale alerts\n"
        "/sentiment – Emoji sentiment score\n"
        "/stealthlaunches – No-social stealth launches"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def max_command(update: Update, context: CallbackContext):
    message = fetch_max_token_data(MAX_TOKEN_ADDRESS)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML", disable_web_page_preview=True)

@restricted
def trending_command(update: Update, context: CallbackContext):
    message = fetch_trending_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def new_command(update: Update, context: CallbackContext):
    message = fetch_new_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def alerts_command(update: Update, context: CallbackContext):
    message = check_suspicious_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def wallets_command(update: Update, context: CallbackContext):
    message = summarize_wallet_activity(WALLETS)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def pnl_command(update: Update, context: CallbackContext):
    message = track_position()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def target_alerts(update: Update, context: CallbackContext):
    message = detect_mirror_wallets()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def sentiment_command(update: Update, context: CallbackContext):
    message = analyze_sentiment()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

@restricted
def stealth_command(update: Update, context: CallbackContext):
    message = find_stealth_launches()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

def send_daily_report():
    try:
        for uid in WHITELIST:
            bot.send_message(chat_id=uid, text=fetch_max_token_data(MAX_TOKEN_ADDRESS), parse_mode="HTML", disable_web_page_preview=True)
            bot.send_message(chat_id=uid, text=fetch_trending_tokens(), parse_mode="HTML")
            bot.send_message(chat_id=uid, text=fetch_new_tokens(), parse_mode="HTML")
            bot.send_message(chat_id=uid, text=check_suspicious_activity(), parse_mode="HTML")
            bot.send_message(chat_id=uid, text=summarize_wallet_activity(WALLETS), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error sending daily report: {e}")

# Command registration
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("trending", trending_command))
dispatcher.add_handler(CommandHandler("new", new_command))
dispatcher.add_handler(CommandHandler("alerts", alerts_command))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("pnl", pnl_command))
dispatcher.add_handler(CommandHandler("targetalerts", target_alerts))
dispatcher.add_handler(CommandHandler("sentiment", sentiment_command))
dispatcher.add_handler(CommandHandler("stealthlaunches", stealth_command))

# Daily report 9AM BKK time
scheduler.add_job(send_daily_report, "cron", hour=9, timezone="Asia/Bangkok")

updater.start_polling()
updater.idle()
