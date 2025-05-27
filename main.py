import logging
from telegram import Update, ParseMode, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
from utils import (
    fetch_max_token_data,
    fetch_trending_tokens,
    fetch_new_tokens,
    check_suspicious_activity,
    summarize_wallet_activity,
    track_position,
    get_target_alerts,
    get_sentiment_score,
    find_stealth_launches,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
TOKEN = config["telegram_token"]
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    message = (
        "🤖 <b>Welcome to SolMadSpecBot!</b>\n"
        "Here’s what I can do:\n\n"
        "/max – MAX token stats\n"
        "/trending – Top 5 Sol meme coins\n"
        "/new – New token launches\n"
        "/alerts – Suspicious activity\n"
        "/wallets – Watchlist summaries\n"
        "/pnl – PnL & break-even\n"
        "/targetalerts – Sell zone hits\n"
        "/sentiment – Emoji sentiment\n"
        "/stealthlaunches – No-social token pings"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def max_command(update: Update, context: CallbackContext):
    try:
        data = fetch_max_token_data()
        message = (
            "🐶 <b>MAX Token Update</b>\n"
            f"💰 Price: ${data['price']:.8f}\n"
            f"🏛️ Market Cap: ${data['market_cap']:,.0f}\n"
            f"📉 Volume (24h): ${data['volume']:,.2f}\n"
            f"🏦 FDV: ${data['fdv']:,.0f}\n"
            f"📊 Buys: {data['buys']} | Sells: {data['sells']}\n"
            f"💧 Liquidity: ${data['liquidity']:,.2f}\n"
            f"📈 24H Change: {data['change']}%\n"
            f"🔢 Holders: {data['holders']}\n"
            f"🕐 Launch Time: {data['launch_time']}\n"
            f"🔗 <a href='{data['dex_url']}'>View on Dexscreener</a>"
        )
        context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"MAX command error: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Unable to fetch MAX token data.")

def trending_command(update: Update, context: CallbackContext):
    message = fetch_trending_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def new_command(update: Update, context: CallbackContext):
    message = fetch_new_tokens()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def alerts_command(update: Update, context: CallbackContext):
    message = check_suspicious_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def wallets_command(update: Update, context: CallbackContext):
    message = summarize_wallet_activity()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def pnl_command(update: Update, context: CallbackContext):
    message = track_position()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def targetalerts_command(update: Update, context: CallbackContext):
    message = get_target_alerts()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)

def sentiment_command(update: Update, context: CallbackContext):
    message = get_sentiment_score()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def stealth_command(update: Update, context: CallbackContext):
    message = find_stealth_launches()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", start))
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("trending", trending_command))
dispatcher.add_handler(CommandHandler("new", new_command))
dispatcher.add_handler(CommandHandler("alerts", alerts_command))
dispatcher.add_handler(CommandHandler("wallets", wallets_command))
dispatcher.add_handler(CommandHandler("pnl", pnl_command))
dispatcher.add_handler(CommandHandler("targetalerts", targetalerts_command))
dispatcher.add_handler(CommandHandler("sentiment", sentiment_command))
dispatcher.add_handler(CommandHandler("stealthlaunches", stealth_command))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "OK"

def send_daily_report():
    logging.info("Daily summary job triggered.")

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=9)
scheduler.start()

if __name__ == "__main__":
    logging.info("Running SolMadSpecBot...")
    app.run(host="0.0.0.0", port=10000)
