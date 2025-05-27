
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from utils import (
    fetch_max_token_data,
    get_trending_coins,
    get_new_tokens,
    check_suspicious_activity,
    get_wallet_activity,
    get_token_scorecard,
    get_recent_launches,
    scan_contract_security,
)
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config["telegram_token"])

def start(update: Update, context: CallbackContext):
    message = """<b>Welcome to SolMadSpecBot!</b>

Use the commands below:
/max – MAX token update
/trending – Top 5 trending SOL meme coins
/new – New token launches (<12h)
/alerts – Suspicious wallet/dev/LP activity
/wallets – Watchlisted wallet activity
/launches – Real-time LP > $10K token launches
/scan – Smart contract scan
/scorecard – Token volume/liquidity score
/socials – Social signal activity
/help – Full command list
"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="HTML"
    )

def help_command(update: Update, context: CallbackContext):
    start(update, context)

def max(update: Update, context: CallbackContext):
    msg = fetch_max_token_data()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def trending(update: Update, context: CallbackContext):
    msg = get_trending_coins()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def new_tokens(update: Update, context: CallbackContext):
    msg = get_new_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def alerts(update: Update, context: CallbackContext):
    msg = check_suspicious_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def wallets(update: Update, context: CallbackContext):
    msg = get_wallet_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def launches(update: Update, context: CallbackContext):
    msg = get_recent_launches()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def scan(update: Update, context: CallbackContext):
    msg = scan_contract_security()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def scorecard(update: Update, context: CallbackContext):
    msg = get_token_scorecard()
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def socials(update: Update, context: CallbackContext):
    msg = "📈 <b>Social Signals</b>\n• Twitter Mentions: +143%\n• TG Growth: +8%\n• Buzz Score: 🔥🔥🔥"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="HTML")

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data == "lookup":
        query.edit_message_text("🔍 Token details loading...")
    elif data == "score":
        query.edit_message_text(get_token_scorecard(), parse_mode="HTML")
    elif data == "scan":
        query.edit_message_text(scan_contract_security(), parse_mode="HTML")

updater = Updater(token=config["telegram_token"], use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("max", max))
dispatcher.add_handler(CommandHandler("trending", trending))
dispatcher.add_handler(CommandHandler("new", new_tokens))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("launches", launches))
dispatcher.add_handler(CommandHandler("scan", scan))
dispatcher.add_handler(CommandHandler("scorecard", scorecard))
dispatcher.add_handler(CommandHandler("socials", socials))
dispatcher.add_handler(CallbackQueryHandler(button_callback))

def main():
    print("Running SolMadSpecBot...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
