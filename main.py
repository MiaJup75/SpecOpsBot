import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
from utils import (
    fetch_max_token_data,
    get_trending_coins,
    fetch_new_tokens,
    check_suspicious_activity,
    track_position,
    fetch_sentiment_score,
    send_target_alerts,
    fetch_wallet_activity,
    fetch_token_classification
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config["telegram_token"]
WHITELIST = config["whitelist"]

bot = Bot(token=TOKEN)
scheduler = BackgroundScheduler()

# Permission
def is_allowed(user_id):
    return str(user_id) in WHITELIST

# Welcome message
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    welcome_text = (
        "<b>Welcome to SolMadSpecBot!</b>\n\n"
        "Commands:\n"
        "• /max – MAX token stats\n"
        "• /trending – Top meme coins\n"
        "• /new – Fresh launches\n"
        "• /alerts – Whale/dev flags\n"
        "• /wallets – Watched wallets\n"
        "• /score – Sentiment scores\n"
        "• /position – PnL & entry\n"
        "• /target – Sell zone alerts\n"
        "• /radar – Stealth tokens\n"
        "• /ai – Trade prompt\n"
        "• /classify – Token narratives\n"
        "• /help – Quick guide"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_text,
        parse_mode=ParseMode.HTML
    )

# Help command
def help_command(update: Update, context: CallbackContext):
    return start(update, context)

# MAX token tracker
def max(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = fetch_max_token_data()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# Trending meme coins
def trending(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = get_trending_coins()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# New tokens
def new(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = fetch_new_tokens()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# Alerts
def alerts(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = check_suspicious_activity()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# Wallet activity
def wallets(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = fetch_wallet_activity()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# Sentiment
def score(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = fetch_sentiment_score()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# Position
def position(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = track_position()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# Targets
def target(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = send_target_alerts()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# Stealth tokens
def radar(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = fetch_new_tokens(stealth_only=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# AI prompt
def ai(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="<b>🧠 AI Trade Prompt (beta)</b>\n🚧 Coming soon.",
        parse_mode=ParseMode.HTML
    )

# Classifier
def classify(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        return
    msg = fetch_token_classification()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML
    )

# Scheduled daily update
def send_daily_report():
    msg = fetch_token_classification(daily=True)
    for user_id in WHITELIST:
        try:
            bot.send_message(chat_id=user_id, text=msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(f"Error sending daily report to {user_id}: {e}")

# Command wiring
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("new", new))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("score", score))
dispatcher.add_handler(CommandHandler("position", position))
dispatcher.add_handler(CommandHandler("target", target))
dispatcher.add_handler(CommandHandler("radar", radar))
dispatcher.add_handler(CommandHandler("ai", ai))
dispatcher.add_handler(CommandHandler("classify", classify))

# Schedule 9AM BKK daily job
scheduler.add_job(send_daily_report, "cron", hour=9, timezone="Asia/Bangkok")
scheduler.start()

if __name__ == "__main__":
    logging.info("Running SolMadSpecBot...")
    updater.start_polling()
    updater.idle()
